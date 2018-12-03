from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import uuid

from hermes.auth import login_required
from hermes.db import get_db

bp = Blueprint('accounts', __name__)


@bp.route('/')
@login_required
def index():
    """Show all the accounts, most recent first."""
    db = get_db()
    transactions = db.execute(
        'SELECT accounts_name, type_name, accounts_code,'
        ' CASE WHEN sum(splits_value) >= 0 THEN sum(splits_value) ELSE 0 END "debit",'
        ' CASE WHEN sum(splits_value) <= 0 THEN sum(splits_value) *-1 ELSE 0 END "credit"'
        ' FROM splits'
        ' JOIN accounts on accounts_id = accounts_id_fk'
        ' JOIN transactions on trans_id = trans_id_fk'
        ' JOIN type on type_id = type_id_fk'
        ' GROUP BY accounts_name, type_name, accounts_code'
        ' HAVING sum(splits_value) <> 0'
        ' ORDER BY accounts_code ASC'
    ).fetchall()

    return render_template('accounts/index.html', transactions=transactions)


@bp.route('/add', methods=('GET', 'POST'))
@login_required
def add_account():

    db = get_db()

    account_types = db.execute(
        'SELECT type_id, type_name'
        ' FROM type'
    ).fetchall()

    if request.method == 'POST':
        name = request.form['name']
        type_id = request.form['type_id']
        code = request.form['code']
        open_date = request.form['open_date']
        mod = int(request.form['dr-cr'])
        open_value = float(request.form['open_value']) * mod
        desc = request.form['desc']
        error = None

        if not name:
            error = 'Name is requied.'
        elif not type_id:
            error = 'Account type is required.'
        elif not code:
            error = 'Nominal code is required.'
        elif db.execute(
            'SELECT accounts_id FROM accounts WHERE accounts_code = ?', (code,)
        ).fetchone() is not None:
            error = 'Code {0} is already used.'.format(code)

        if error is not None:
            flash(error)
        else:

            accounts_id = str(uuid.uuid4())
            trans_id = str(uuid.uuid4())

            suspense = db.execute(
                'SELECT accounts_id FROM accounts WHERE accounts_code = 9999'
            ).fetchone()

            db.execute(
                'INSERT INTO accounts (accounts_id, accounts_name, accounts_code, type_id_FK, accounts_desc)'
                ' VALUES (?, ?, ?, ?, ?)',
                (accounts_id, name, code, type_id, desc)
            )

            db.execute(
                'INSERT INTO transactions (trans_id, trans_date, trans_desc)'
                ' VALUES (?, ?, ?)',
                (trans_id, open_date, "Opening Balance - " + str(code))
            )

            splits_id = str(uuid.uuid4())
            db.execute(
                'INSERT INTO splits (splits_id, trans_id_fk, accounts_id_fk, splits_value)'
                ' VALUES (?, ?, ?, ?)',
                (splits_id, trans_id, accounts_id, open_value)
            )

            splits_id = str(uuid.uuid4())
            db.execute(
                'INSERT INTO splits (splits_id, trans_id_fk, accounts_id_fk, splits_value)'
                ' VALUES (?, ?, ?, ?)',
                (splits_id, trans_id, suspense['accounts_id'], open_value * -1)
            )
            db.commit()
            return redirect(url_for('accounts.index'))

    return render_template('accounts/add.html', account_types=account_types)


@bp.route('/settings')
@login_required
def settings():
    return render_template('accounts/settings.html')
