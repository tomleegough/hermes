from flask import (
    Blueprint, g, request, session
)

from hermes.db import get_db
from uuid import uuid4

import datetime
import random

bp = Blueprint('queries', __name__)

# Categories
def category_values_for_current_org():
    # SUM value of transactions for given category
    db = get_db()

    category_values = db.execute(
        'SELECT'
        '   *, '
        ' CASE'
        '   WHEN sum(trans_value_net) is Null THEN 0'
        '   ELSE sum(trans_value_net)'
        '   END AS "value"'
        ' FROM'
        '   categories'
        ' LEFT JOIN'
        '   transactions on category_id_fk = category_id'
        ' JOIN'
        '   category_type on cat_type_id = cat_type_id_fk'
        ' WHERE'
        '   categories.org_id_fk = ?'
        ' GROUP BY'
        '   category_id'
        ' ORDER BY'
        '   cat_type_order ASC,'
        '   value DESC',
        (
            session['current_org'],
        )
    ).fetchall()

    return category_values


def get_transactions_for_category(category_id):
    db = get_db()

    transactions = db.execute(
        'SELECT'
        '   *'
        ' FROM'
        '   transactions'
        ' JOIN'
        '   user on user_id = user_id_fk'
        ' WHERE'
        '   org_id_fk = ? and'
        '   category_id_fk = ?',
        (
            session['current_org'],
            category_id,
        )
    ).fetchall()

    return transactions


def get_all_categories_for_org():
    db = get_db()

    categories = db.execute(
        'SELECT'
        '   *'
        ' FROM'
        '   categories'
        ' JOIN'
        '   category_type on cat_type_id = cat_type_id_fk'
        ' WHERE'
        '   org_id_fk = ?',
        (
            session['current_org'],
        )
    ).fetchall()

    return categories


def get_category_by_id(cat_id):
    db = get_db()

    category = db.execute(
        'SELECT'
        '   *'
        ' FROM'
        '   categories'
        ' WHERE'
        '   category_id = ?',
        (
            cat_id,
        )
    ).fetchone()

    return category


def change_category_status(status_flag, cat_id):
    db = get_db()

    db.execute(
        'UPDATE'
        '   categories'
        ' SET'
        '   category_enabled_flag = ?'
        ' WHERE'
        '   category_id = ?',
        (
            status_flag,
            cat_id,
        )
    )

    db.commit()


def change_org_status(org_id):
    db = get_db()

    org = get_org_by_id(org_id)

    status_flag = org['org_enabled_flag']

    if status_flag == 0:
        status_flag = 1
    else:
        status_flag = 0

    db.execute(
        'UPDATE'
        '   organisation'
        ' SET'
        '   org_enabled_flag = ?'
        ' WHERE'
        '   org_id = ?',
        (
            status_flag,
            org_id,
        )
    )

    db.commit()


def create_category(form_data):
    db = get_db()

    cat_id = str(uuid4())

    db.execute(
        'INSERT INTO categories ('
        '   category_id,'
        '   category_name,'
        '   category_enabled_flag,'
        '   org_id_fk,'
        '   cat_type_id_fk'
        ') VALUES ('
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?'
        ' )',
        (
            cat_id,
            form_data['cat_name'],
            form_data['active_flag'],
            session['current_org'],
            form_data['type_id'],
        )
    )

    db.commit()

    return cat_id


def update_category(form_data, cat_id):
    db = get_db()

    db.execute(
        'UPDATE'
        '   categories'
        ' SET'
        '   category_name = ?,'
        '   category_enabled_flag = ?, '
        '   cat_type_id_fk = ?'
        ' WHERE'
        '   category_id = ?',
        (
            form_data['cat_name'],
            form_data['active_flag'],
            form_data['type_id'],
            cat_id,
        )
    )

    db.commit()


def get_category_types():
    db = get_db()

    cat_types = db.execute(
        'SELECT'
        '   *'
        ' FROM'
        '   category_type'
    ).fetchall()

    return cat_types


def get_all_orgs_for_current_user():
    db = get_db()

    organisations = db.execute(
        'SELECT'
        '   *'
        ' FROM'
        '   organisation'
        ' JOIN'
        '   user_organisation on org_id = org_id_fk'
        ' LEFT JOIN'
        '   organisation_type on org_type = org_type_id'
        ' WHERE'
        '   user_id_fk = ?',
        (
            session['user_id'],
        )
    ).fetchall()

    return organisations


def get_active_orgs_for_current_user():
    db = get_db()

    orgs = db.execute(
        'SELECT'
        '   *'
        ' FROM'
        '   organisation'
        ' JOIN'
        '   user_organisation on org_id = org_id_fk'
        ' WHERE'
        '   user_id_fk = ? and'
        '   org_enabled_flag = 1',
        (
            session['user_id'],
        )
    ).fetchall()

    return orgs


def create_organisation(form_data):
    db = get_db()

    org_id = str(uuid4())

    db.execute(
        'INSERT INTO organisation ('
        '   org_id,'
        '   org_name,'
        '   org_enabled_flag,'
        '   org_vat,'
        '   org_number,'
        '   org_type'
        ' ) VALUES ('
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?'
        ' )',
        (
            org_id,
            form_data['org_name'],
            form_data['org_enabled_flag'],
            form_data['org_vat'],
            form_data['org_no'],
            form_data['org_type']
        )
    )

    add_org_permissions(
        g.user['user_id'],
        org_id,
    )

    db.commit()

    return org_id


def get_organisation_types():
    db = get_db()

    org_types = db.execute(
        'SELECT *'
        ' FROM organisation_type'
    )

    return org_types


def add_org_permissions(user_id, org_id):
    # add user permissions for own organisations
    db = get_db()

    db.execute(
        'INSERT INTO user_organisation ('
        '   user_id_fk,'
        '   org_id_fk'
        ' ) VALUES ('
        '   ?,'
        '   ?'
        ' )',
        (
            user_id,
            org_id,
        )
    )

    db.commit()


def update_organistation(form_data, org_id):
    db = get_db()

    db.execute(
        'UPDATE'
        '   organisation'
        ' SET'
        '   org_name = ?,'
        '   org_enabled_flag = ?,'
        '   org_type = ?,'
        '   org_vat = ?,'
        '   org_number = ?'
        ' WHERE'
        '   org_id = ?',
        (
            form_data['org_name'],
            form_data['org_enabled_flag'],
            form_data['org_type'],
            form_data['org_vat'],
            form_data['org_no'],
            org_id,
        )
    )

    db.commit()


def get_org_by_id(org_id):
    db = get_db()

    org = db.execute(
        'SELECT'
        '   *'
        ' FROM'
        '   organisation'
        ' WHERE'
        '   org_id = ?',
        (
            org_id,
        )
    ).fetchone()

    return org


def get_bank_accounts_for_current_org():
    db = get_db()

    accounts = db.execute(
        'SELECT'
        '   bank_id,'
        '   bank_name,'
        '   bank_reference,'
        '   bank_enabled_flag,'
        '   bank_currency_code,'
        '   round('
        '       sum( '
        '           IFNULL(trans_value_net, 0) +'
        '           IFNULL(trans_value_vat, 0)'
        '       ), 2       '
        '   ) as "bank_balance"'
        ' FROM'
        '   bank'
        ' LEFT JOIN'
        '   transactions on bank_id = bank_id_fk'
        ' WHERE'
        '   bank.org_id_fk = ?'
        ' GROUP BY'
        '   bank_id',
        (
            session['current_org'],
        )
    ).fetchall()

    return accounts


def create_bank_account(form_data, org_id):
    db = get_db()

    bank_id = str(uuid4())

    if org_id == '':
        org_id = session['current_org']

    db.execute(
        'INSERT INTO bank ('
        '   bank_id,'
        '   bank_name,'
        '   bank_reference,'
        '   bank_created_date,'
        '   bank_enabled_flag,'
        '   bank_currency_code,'
        '   org_id_fk'
        ' ) VALUES ('
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?'
        ' )',
        (
            bank_id,
            form_data['bank_name'],
            form_data['bank_reference'],
            datetime.datetime.now().strftime('%Y-%m-%d'),
            form_data['bank_enabled_flag'],
            form_data['bank_currency_code'],
            org_id
        )
    )

    vat_type = db.execute(
        'SELECT vat_type_id'
        ' FROM'
        '  vat_type'
        ' WHERE'
        '  vat_type_name = "Out of Scope"'
    ).fetchone()

    db.commit()

    o_bal = {
        'trans_date': form_data['open_date'],
        'trans_desc': 'Opening Balance',
        'trans_value_net': form_data['open_balance'],
        'trans_value_vat': 0.00,
        'sign': 1,
        'org_id_fk': org_id,
        'trans_created_date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'bank_id': bank_id,
        'cat_id': '',
        'vat_type_id_fk': vat_type['vat_type_id']
    }

    create_transaction(o_bal)

    return bank_id


def create_transaction(trans_data):
    db = get_db()

    db.execute(
        'INSERT INTO transactions ('
        '   trans_id,'
        '   trans_post_date,'
        '   trans_created_date,'
        '   trans_value_net,'
        '   trans_value_vat,'
        '   trans_description,'
        '   user_id_fk,'
        '   org_id_fk,'
        '   bank_id_fk,'
        '   category_id_fk,'
        '   vat_type_id_fk'
        ' ) VALUES ('
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?,'
        '   ?'
        ')',
        (
            str(uuid4()),
            trans_data['trans_date'],
            datetime.datetime.now().strftime('%Y-%m-%d'),
            float(trans_data['trans_value_net']) * float(trans_data['sign']),
            float(trans_data['trans_value_vat']) * float(trans_data['sign']),
            trans_data['trans_desc'],
            session['user_id'],
            session['current_org'],
            trans_data['bank_id'],
            trans_data['cat_id'],
            trans_data['vat_type_id_fk'],
        )
    )

    db.commit()

def get_bank_account(bank_id):
    db = get_db()

    account = db.execute(
        'SELECT'
        '   *'
        ' FROM'
        '   bank'
        ' WHERE'
        '   bank_id = ?',
        (
            bank_id,
        )
    ).fetchone()

    return account

def update_bank_details(bank_data, bank_id):
    db = get_db()

    db.execute(
        'UPDATE'
        '   bank'
        ' SET'
        '   bank_name = ?,'
        '   bank_reference = ?,'
        '   bank_created_date = ?,'
        '   bank_enabled_flag = ?,'
        '   bank_currency_code = ?'
        ' WHERE'
        '   bank_id = ?',
        (
            bank_data['bank_name'],
            bank_data['bank_reference'],
            datetime.datetime.now().strftime('%Y-%m-%d'),
            bank_data['bank_enabled_flag'],
            bank_data['bank_currency_code'],
            bank_id,
        )
    )

    db.commit()

def get_active_categories_for_current_org():
    db = get_db()

    categories = db.execute(
        "SELECT"
        "   *"
        " FROM"
        "   categories"
        " WHERE"
        "   org_id_fk = ? and"
        "   category_enabled_flag = 1",
        (
            session['current_org'],
        )
    ).fetchall()

    return categories


def dashboard_graph():
    db = get_db()

    from_date = datetime.datetime.now() - datetime.timedelta(days=365)
    from_date = datetime.datetime.strftime(from_date, '%Y-%m-%d')

    values = db.execute(
        'SELECT'
        '   strftime("%Y-%m-", trans_post_date)||"01" as period,'
        '   sum(trans_value_net) as value'
        ' FROM'
        '   transactions'
        ' JOIN'
        '   categories on category_id = category_id_fk'
        ' JOIN'
        '   category_type on cat_type_id = cat_type_id_fk'
        ' WHERE'
        '   transactions.org_id_fk=? and'
        '   cat_type_name = "Income" and'
        '   trans_post_date >= ?'
        ' GROUP BY'
        '   cat_type_name,'
        '   period'
        ' ORDER BY'
        '   period',
        (
            session['current_org'],
            from_date,
        )
    ).fetchall()

    return values


def get_vat_codes():
    db = get_db()

    vat_codes = db.execute(
        'SELECT *'
        ' FROM vat_type'
    ).fetchall()

    return vat_codes


def create_standard_coa(coa):
    db = get_db()

    fixed_asset = db.execute(
        'SELECT cat_type_id'
        ' FROM category_type'
        ' WHERE cat_type_name = "Fixed Assets"'
    ).fetchone()

    current_asset = db.execute(
        'SELECT cat_type_id'
        ' FROM category_type'
        ' WHERE cat_type_name = "Current Liabilities"'
    ).fetchone()

    current_liability = db.execute(
        'SELECT cat_type_id'
        ' FROM category_type'
        ' WHERE cat_type_name = "Current Liabilities"'
    ).fetchone()

    long_term_liability = db.execute(
        'SELECT cat_type_id'
        ' FROM category_type'
        ' WHERE cat_type_name = "Long-term Liabilities"'
    ).fetchone()

    income = db.execute(
        'SELECT cat_type_id'
        ' FROM category_type'
        ' WHERE cat_type_name = "Income"'
    ).fetchone()

    expense = db.execute(
        'SELECT cat_type_id'
        ' FROM category_type'
        ' WHERE cat_type_name = "Expense"'
    ).fetchone()

    equity = db.execute(
        'SELECT cat_type_id'
        ' FROM category_type'
        ' WHERE cat_type_name = "Equity"'
    ).fetchone()

    if coa == 'individual':
        fixed_asset_categories = [
            'House',
            'Motor vehicles',
            'Pension'
        ]

        for each in fixed_asset_categories:
            category = {
                'cat_name': each,
                'active_flag': 1,
                'type_id': fixed_asset['cat_type_id']
            }

            create_category(category)

        liability_categories = [
            'Mortgage'
        ]

        for each in liability_categories:
            category = {
                'cat_name': each,
                'active_flag': 1,
                'type_id': long_term_liability['cat_type_id']
            }

            create_category(category)

        income_categories = [
            'Salary',
            'Interest'
        ]

        for each in income_categories:
            category = {
                'cat_name': each,
                'active_flag': 1,
                'type_id': income['cat_type_id']
            }

            create_category(category)

        expense_categories = [
            'Rent',
            'Utilities',
            'Phone',
            'Internet',
            'Insurance',
            'Food',
            'Holiday',
            'Socializing',
            'Other Expenses'
        ]

        for each in expense_categories:
            category = {
                'cat_name': each,
                'active_flag': 1,
                'type_id': expense['cat_type_id']
            }

            create_category(category)

    if coa == 'limited':
        fixed_asset_categories = [
            'Plant and Machinery',
            'Motor Vehicles',
            'Fixtures and Fittings'
        ]

        for each in fixed_asset_categories:
            category = {
                'cat_name': each,
                'active_flag': 1,
                'type_id': fixed_asset['cat_type_id']
            }

            create_category(category)

        asset_categories = [
            'Debtors',
            'Stock',
            'Prepayments'
        ]

        for each in asset_categories:
            category = {
                'cat_name': each,
                'active_flag': 1,
                'type_id': current_asset['cat_type_id']
            }

            create_category(category)

        current_liability_categories = [
            'Creditors',
            'Deferred Income',
            'Taxes',
            'Accruals'
        ]

        for each in current_liability_categories:
            category = {
                'cat_name': each,
                'active_flag': 1,
                'type_id': current_liability['cat_type_id']
            }

            create_category(category)

        long_liability_categories = [
            'Bank Loans',
            'Directors Loan Account',
            'Corporation Tax'
        ]

        for each in long_liability_categories:
            category = {
                'cat_name': each,
                'active_flag': 1,
                'type_id': long_term_liability['cat_type_id']
            }

            create_category(category)

        income_categories = [
            'Sales',
            'Other Income'
        ]

        for each in income_categories:
            category = {
                'cat_name': each,
                'active_flag': 1,
                'type_id': income['cat_type_id']
            }

            create_category(category)

        expense_categories = [
            'Cost of Goods Sold',
            'Rent and Rates',
            'Utilities',
            'Wages and Salaries',
            'Travel Expenses',
            'IT and Telecomms',
            'Stationary and Postage',
            'Professional and Legal Fees',
            'Other Expenses',
            'Depreciation',
            'Tax'
        ]

        for each in expense_categories:
            category = {
                'cat_name': each,
                'active_flag': 1,
                'type_id': expense['cat_type_id']
            }

            create_category(category)


    db.commit()


def add_demo_data():
    db = get_db()

    org_type = db.execute(
        'SELECT * FROM organisation_type'
        ' WHERE org_type_name = "Limited Company"'
    ).fetchone()

    demo_org = {
        "org_name": 'Hermes Demo Ltd',
        "org_enabled_flag": 1,
        "org_vat": "12 3456 789 GB",
        "org_no": "12345678",
        "org_type": org_type['org_type_id']
    }

    org_id = create_organisation(demo_org)

    bank_accounts = [
        {
            'bank_name': 'Business Bank Account',
            'bank_reference': 00-00-00-10000001,
            'bank_enabled_flag': 1,
            'bank_currency_code': 'gbp',
            'open_date': datetime.date(2019, 1, 1),
            'open_balance': round(random.random() * 10000, 2)
        },

        {
            'bank_name': 'Overdrawn Account',
            'bank_reference': 00 - 00 - 00 - 10000002,
            'bank_enabled_flag': 1,
            'bank_currency_code': 'gbp',
            'open_date': datetime.date(2019, 1, 1),
            'open_balance': round(random.random() * 1000, 2) * -1
        },

        {
            'bank_name': 'Savings Account',
            'bank_reference': 00 - 00 - 00 - 10000002,
            'bank_enabled_flag': 1,
            'bank_currency_code': 'gbp',
            'open_date': datetime.date(2019, 1, 1),
            'open_balance': round(random.random() * 100000, 2)
        }

    ]

    for bank in bank_accounts:
        bank_id = create_bank_account(bank, org_id)

    db.commit()
