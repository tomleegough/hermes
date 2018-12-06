from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from uuid import uuid4
from datetime import datetime

from hermes.auth import login_required
from hermes.db import get_db

bp = Blueprint('banking', __name__, url_prefix='/bank')


@bp.route('/')
def show_accounts():
    db = get_db()

    accounts = db.execute(
        'SELECT * FROM bank WHERE org_id_fk=?',
        (session['current_org'],)
    ).fetchall()

    return render_template('tables/accounts.html', accounts=accounts)


@bp.route('/<action>/', defaults={'bank_id': ''}, methods=['POST', 'GET'])
@bp.route('/<action>/<bank_id>', methods=['POST', 'GET'])
@login_required
def account(action, bank_id):
    db = get_db()

    if request.method == 'POST':
        bank_name = request.form['bank_name']
        bank_reference = request.form['bank_reference']
        bank_created_date = datetime.now().strftime('%Y-%m-%d')
        if 'bank_enabled_flag' not in request.form:
            bank_enabled_flag = 0
        else:
            bank_enabled_flag = request.form['bank_enabled_flag']
        bank_currency_code = request.form['bank_currency_code']

    if request.method == 'POST' and action == 'add':
        bank_id = str(uuid4())
        org_id_fk = session['current_org']


        db.execute(
            'INSERT INTO bank (bank_id, bank_name, bank_reference,'
            ' bank_created_date, bank_created_date, bank_enabled_flag,'
            ' bank_currency_code, org_id_fk)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (bank_id, bank_name, bank_reference, bank_created_date,
                bank_created_date, bank_enabled_flag,
                bank_currency_code, org_id_fk,)
        )

        db.commit()

        return redirect(url_for('banking.show_accounts'))

    if request.method == 'POST' and action == 'edit':
        db.execute(
            'UPDATE bank'
            ' SET bank_name=?,'
            ' bank_reference=?,'
            ' bank_created_date=?,'
            ' bank_created_date=?,'
            ' bank_enabled_flag=?,'
            ' bank_currency_code=?'
            ' WHERE bank_id=?',
            (bank_name, bank_reference, bank_created_date,
                bank_created_date, bank_enabled_flag,
                bank_currency_code, bank_id,)
        )

        db.commit()

        return redirect(url_for('banking.show_accounts'))

    account = db.execute(
        'SELECT * FROM bank WHERE bank_id=?',
        (bank_id,)
    ).fetchone()

    return render_template('forms/account.html', account=account, action=action)
