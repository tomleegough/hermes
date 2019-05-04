from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from uuid import uuid4
from datetime import datetime

from hermes.auth import login_required
from hermes.db import get_db
import hermes.queries as queries

bp = Blueprint('banking', __name__, url_prefix='/bank')


@bp.route('/')
def show_accounts():
    accounts = bank_values()
    return render_template('cards/accounts.html', accounts=accounts)


def bank_values():
    db = get_db()

    accounts = db.execute(
        'SELECT bank_id, bank_name, bank_reference,'
        ' bank_enabled_flag, bank_currency_code,'
        ' sum(trans_value) as "bank_balance"'
        ' FROM bank'
        ' LEFT JOIN transactions on bank_id = bank_id_fk'
        ' WHERE bank.org_id_fk=?'
        ' GROUP BY bank_id',
        (session['current_org'],)
    ).fetchall()

    return accounts


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

        trans_id = str(uuid4())
        trans_description = 'Opening Balance'
        trans_created_date = datetime.now().strftime('%Y-%m-%d')
        user_id_fk = session['user_id']
        trans_post_date = request.form['open_date']
        trans_value = request.form['open_balance']

        db.execute(
            'INSERT INTO transactions'
            ' (trans_id, trans_post_date, trans_created_date,'
            ' trans_value, trans_description, user_id_fk,'
            ' org_id_fk, bank_id_fk)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (trans_id, trans_post_date, trans_created_date,
             trans_value, trans_description, user_id_fk,
             org_id_fk, bank_id,)
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

    return render_template(
        'forms/account.html',
        account=account,
        action=action
    )


@bp.route('/transaction/<action>/', defaults={'bank_id': ''}, methods=['POST', 'GET'])
@bp.route('/transaction/<action>/<bank_id>/', methods=['POST', 'GET'])
@login_required
def transaction(action, bank_id):

    db = get_db()

    categories = db.execute(
        "SELECT * FROM categories WHERE org_id_fk = ? and category_enabled_flag = 1",
        (session['current_org'],)
    ).fetchall()

    if action == 'add':
        if bank_id == '':
            accounts = db.execute(
                'SELECT * FROM bank WHERE org_id_fk = ?',
                (session['current_org'],)
            ).fetchall()

        if request.method == 'POST':
            trans_post_date = request.form['trans_date']
            trans_value = request.form['trans_value'] * request.form['sign']
            trans_description = request.form['trans_desc']
            category_id_fk = request.form['cat_id']

            trans_id = str(uuid4())
            trans_created_date = datetime.now().strftime('%Y-%m-%d')
            user_id_fk = session['user_id']
            org_id_fk = session['current_org']

            if bank_id == '':
                bank_id_fk = request.form['bank_id']
            else:
                bank_id_fk = bank_id

            db.execute(
                'INSERT INTO transactions'
                ' (trans_id, trans_post_date, trans_created_date,'
                ' trans_value, trans_description, user_id_fk,'
                ' org_id_fk, bank_id_fk, category_id_fk)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (trans_id, trans_post_date, trans_created_date,
                    trans_value, trans_description, user_id_fk,
                    org_id_fk, bank_id_fk, category_id_fk,)
            )

            db.commit()
            return redirect(url_for('banking.show_accounts'))

        return render_template(
            'forms/transaction.html',
            action=action,
            categories=categories,
            accounts=accounts,
            bank_id=bank_id
        )
