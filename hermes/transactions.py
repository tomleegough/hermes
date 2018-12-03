from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import uuid

from hermes.auth import login_required
from hermes.db import get_db

bp = Blueprint('transactions', __name__)


@bp.route('/transactions/view')
@login_required
def view_all():

    db = get_db()

    transactions = db.execute(
        'SELECT trans_date, trans_desc, accounts_code,'
        ' CASE WHEN splits_value >= 0 THEN splits_value ELSE 0 END "debit",'
        ' CASE WHEN splits_value <= 0 THEN splits_value*-1 ELSE 0 END "credit"'
        ' FROM transactions'
        ' JOIN accounts on accounts_id = accounts_id_fk'
        ' JOIN splits on trans_id = trans_id_fk'
        ' ORDER BY trans_date DESC'
    ).fetchall()

    return render_template('transactions/view.html', transactions=transactions)


@bp.route('/transactions/view/<code>')
@login_required
def view(code):
    db = get_db()

    db.execute(
        'DROP TABLE transfers'
    )

    db.execute(
        'CREATE TABLE transfers AS'
        ' SELECT trans_id, accounts_code'
        ' FROM splits'
        ' JOIN accounts on accounts_id = accounts_id_fk'
        ' JOIN transactions on trans_id = trans_id_fk'
        ' WHERE accounts_code <> ?',
        (code,)
    )
    transactions = db.execute(
        ' SELECT trans_date, trans_desc, transfers.accounts_code as accounts_code,'
        ' CASE WHEN splits_value >= 0 THEN splits_value ELSE 0 END "debit",'
        ' CASE WHEN splits_value <= 0 THEN splits_value*-1 ELSE 0 END "credit"'
        ' FROM transactions'
        ' JOIN splits on transactions.trans_id = splits.trans_id_fk'
        ' JOIN accounts on accounts.accounts_id = splits.accounts_id_fk'
        ' JOIN transfers on transfers.trans_id = transactions.trans_id'
        ' WHERE accounts.accounts_code = ?',
        (code,)
    )

    return render_template('transactions/view.html', transactions=transactions)


@bp.route('/transactions/add', methods=('GET', 'POST'))
@login_required
def add_transaction():

    db = get_db()

    account_types = db.execute(
        'SELECT accounts_id, accounts_name, accounts_code'
        ' FROM accounts'
        ' ORDER BY accounts_code ASC'
    ).fetchall()

    if request.method == 'POST':
        source_code = request.form['source_code']
        transfer_code = request.form['transfer_code']
        description = request.form['description']
        mod = int(request.form['dr-cr'])
        value = float(request.form['value']) * mod
        trans_date = request.form['trans_date']
        error = None

        if not trans_date:
            error = 'Date is requied.'
        elif not transfer_code:
            error = 'Nominal code is required.'
        elif not description:
            error = 'Description is required.'
        elif not value:
            error = 'Value requred'

        if error is not None:
            flash(error)
        else:
            source_code = db.execute(
                'SELECT accounts_id, accounts_code'
                ' FROM accounts'
                ' WHERE accounts_code = ?',
                (source_code,)
            ).fetchone()

            transfer_code = db.execute(
                'SELECT accounts_id'
                ' FROM accounts'
                ' WHERE accounts_code = ?',
                (transfer_code,)
            ).fetchone()

            trans_id = str(uuid.uuid4())

            db.execute(
                'INSERT INTO transactions (trans_id, trans_date, trans_desc)'
                ' VALUES (?, ?, ?)',
                (trans_id, trans_date, description)
            )

            splits_id = str(uuid.uuid4())
            db.execute(
                'INSERT INTO splits (splits_id, trans_id_fk, accounts_id_fk, splits_value)'
                ' VALUES (?, ?, ?, ?)',
                (splits_id, trans_id, source_code['accounts_id'], value)
            )

            splits_id = str(uuid.uuid4())
            db.execute(
                'INSERT INTO splits (splits_id, trans_id_fk, accounts_id_fk, splits_value)'
                ' VALUES (?, ?, ?, ?)',
                (splits_id, trans_id, transfer_code['accounts_id'], value * -1)
            )
            db.commit()
            return redirect(url_for('transactions.view', code=source_code['accounts_code']))

    return render_template('transactions/add.html', account_types=account_types)
