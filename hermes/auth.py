import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from hermes.db import get_db
from uuid import uuid4
from hermes.mail import (
    send_verification_email, send_password_reset
)
import hermes.core_queries as queries
import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def group_admin(view):
    """View decorator that checks the user group is admin."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        db = get_db()

        user = db.execute(
            'SELECT * FROM user WHERE user_id = ?',
            (session['user_id'],)
        ).fetchone()

        if user['user_group'] != 'admin':
            return redirect(url_for('accounts.index'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE user_id = ?', (user_id,)
        ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == 'POST':
        username = str.lower(request.form['username'])
        password = request.form['password']
        # email = request.form['user_email']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif request.form['password'] != request.form['password_verify']:
            error = 'Passwords do not match'
        elif db.execute(
            'SELECT user_id FROM user WHERE user_name = ?', (username,)
        ).fetchone() is not None:
            error = 'User {0} is already registered.'.format(username)

        if error is None:
            # the name is available, store it in the database and go to
            # the login page

            user_activate_url = str(uuid4())
            user_id = str( uuid4())

            db.execute(
                'INSERT INTO user('
                '   user_id,'
                '   user_name,'
                '   user_pass,'
                '   user_enabled_flag,'
                '   user_activated_flag,'
                '   user_activate_url,'
                '   user_activate_url_expiry,'
                '   user_created_date'
                ' ) VALUES ('
                '   ?, ?, ?, ?, ?, ?, ?, ?'
                ' )',
                (
                    user_id,
                    username,
                    generate_password_hash( password ),
                    1,
                    0,
                    user_activate_url,
                    ( datetime.datetime.now() + datetime.timedelta(days=1) ).strftime('%Y-%m-%d'),
                    datetime.datetime.now().strftime('%Y-%m-%d')
                )
            )

            db.execute(
                'INSERT INTO settings (user_id_fk, settings_theme) VALUES (?, "flatly.css")',
                (
                    user_id,
                )
            )

            db.commit()

            send_verification_email(username, user_activate_url)

            return redirect(
                url_for('auth.login')
            )

        flash(error)

    return render_template(
        'auth/register.html'
    )


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Login a registered user by adding the user id to the session."""
    if request.method == 'POST':
        username = str.lower(request.form['username'])
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE user_name = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username or password.'
        elif not check_password_hash(user['user_pass'], password):
            error = 'Incorrect username or password.'
        elif user['user_activated_flag'] == 0:
            error = 'User not activated'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['user_id'] = user['user_id']
            session['id'] = str(uuid4())
            update_orgs()
            session['current_org'] = user['user_last_org_id']
            theme = db.execute(
                'SELECT * FROM user JOIN settings on user_id = user_id_fk WHERE user_id_fk=?',
                (user['user_id'],)
            ).fetchone()
            # if theme['settings_theme'] is not None or theme['settings_theme'] != '':
            #     session['theme'] = theme['settings_theme']
            # else:
            #     session['theme'] = 'flatly.css'
            session['group'] = user['user_group']
            return redirect(
                url_for('index')
            )
        
        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    """Clear the current session, including the stored user id."""

    if 'current_org' in session:

        db = get_db()

        db.execute(
            'UPDATE user SET user_last_org_id = ? WHERE user_id = ?',
            (session['current_org'], session['user_id'],)
        )

        db.commit()

    session.clear()
    return redirect(
        url_for('index')
    )


@bp.route('/change', methods=['GET', 'POST'])
def change_pass():
    db = get_db()

    if request.method == 'POST':

        user = db.execute(
            'SELECT * FROM user WHERE user_id = ?', (session['user_id'],)
        ).fetchone()

        username = user['user_name']
        password = user['user_pass']
        old_pass = request.form['old_password']
        new_pass = request.form['new_password']
        conf_pass = request.form['confirm_password']

        if new_pass != conf_pass:
            error = 'Passwords do not match'
        if old_pass is None or new_pass is None or conf_pass is None:
            error = 'Password cannot be blank'
        if not check_password_hash(old_pass, password):
            error = 'Incorrect password.'

        if error is not None:
            db.execute(
                'UPDATE user'
                ' SET user_pass = ?'
                ' WHERE user_name = ?',
                (generate_password_hash(new_pass), username,)
            )

            db.commit()

            return render_template('auth/success.html')

    return render_template('auth/change.html')


@bp.route('/activate', methods=('POST', 'GET'))
def activate_user():

    if request.method == 'POST':

        db = get_db()

        db.execute(
            'UPDATE'
            '    user'
            ' SET'
            '    user_activated_flag = 1'
            ' WHERE'
            '   user_name = ? and'
            '   user_activate_url = ? and'
            '   user_activate_url_expiry >= ?',
            (
                request.form['username'],
                request.form['activate_code'],
                datetime.datetime.now().strftime('%Y-%m-%d')
            )
        )

        db.commit()

        return redirect(
            url_for(
                'auth.login'
            )
        )

    return render_template(
        'auth/activate.html'
    )

@bp.route('/request_reset', methods=['POST', 'GET'])
def request_reset():

    if request.method == 'POST':
        temp_pass = str(uuid4())
        db = get_db()
        db.execute(
            'UPDATE'
            '   user'
            '  SET'
            '   user_pass = ?,'
            '   user_activated_flag = 0'
            '  WHERE'
            '   user_name = ?',
            (
                generate_password_hash(temp_pass),
                request.form['username']
            )
        )

        db.commit()

        send_password_reset(
            request.form['username'],
            temp_pass
        )

        return redirect(
            url_for(
                'accounts.index'
            )
        )

    return render_template(
        'auth/request-reset.html'
    )

@bp.route('/reset', methods=['POST', 'GET'])
def reset_password():
    db = get_db()

    if request.method == 'POST':
        username = request.form['user_name']

        user = db.execute(
            'SELECT * FROM user WHERE user_name = ?',
            (
                username,
            )
        ).fetchone()

        password = user['user_pass']
        old_pass = request.form['old_password']
        new_pass = request.form['new_password']
        conf_pass = request.form['confirm_password']

        if new_pass != conf_pass:
            error = 'Passwords do not match'
        if old_pass is None or new_pass is None or conf_pass is None:
            error = 'Password cannot be blank'
        if not check_password_hash(old_pass, password):
            error = 'Incorrect password.'

        if error is not None:
            db.execute(
                'UPDATE user'
                ' SET user_pass = ?,'
                ' user_activated_flag = 1'
                ' WHERE user_name = ?',
                (generate_password_hash(new_pass), username,)
            )

            db.commit()

            return render_template('auth/success.html')

    return render_template(
        'auth/change.html'
    )

def update_orgs():
    orgs = queries.get_active_orgs_for_current_user()

    session['orgs'] = []

    for org in orgs:
        session['orgs'].append(
            {
                'org_id': org['org_id'],
                'org_name': org['org_name'],
                'org_vat_flag': org['org_vat_flag'],
            }
        )
