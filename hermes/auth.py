import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from hermes.db import get_db
from hermes.session import update_orgs

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

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


# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     """Register a new user.

#     Validates that the username is not already taken. Hashes the
#     password for security.
#     """
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = get_db()
#         error = None

#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'
#         elif db.execute(
#             'SELECT id FROM user WHERE username = ?', (username,)
#         ).fetchone() is not None:
#             error = 'User {0} is already registered.'.format(username)

#         if error is None:
#             # the name is available, store it in the database and go to
#             # the login page
#             db.execute(
#                 'INSERT INTO user (user_name, user_pass) VALUES (?, ?)',
#                 (username, generate_password_hash(password))
#             )
#             db.commit()
#             return redirect(url_for('auth.login'))

#         flash(error)

#     return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE user_name = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['user_pass'], password):
            error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['user_id'] = user['user_id']
            update_orgs()
            session['current_org'] = user['user_last_org_id']

            return redirect(url_for('index'))

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
    return redirect(url_for('index'))


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

    return render_template('auth/change.html')
