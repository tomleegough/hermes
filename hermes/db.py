import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

from werkzeug.security import check_password_hash, generate_password_hash

from uuid import uuid4
import datetime
import random

def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    db.execute(
        'INSERT INTO user'
        '  (user_id, user_name, user_pass, user_enabled_flag)'
        ' VALUES'
        '  (?,?,?,?)',
        (str(uuid4()), 'admin', generate_password_hash('admin'), 1)
    )

    cat_types = [
        (str(uuid4()), 'Income'),
        (str(uuid4()), 'Expense')
    ]

    for cat_type in cat_types:
        db.execute(
            'INSERT INTO category_type (cat_type_id, cat_type_name)'
            ' VALUES (?, ?)',
            cat_type
        )

    db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


# Generate test data for use in  Hermes
@click.command('generate-data')
@with_appcontext
def generate_test_data():

    db = get_db()

    org_id = str(uuid4())
    user_id = str(uuid4())

    # Generate the user
    db.execute(
        'INSERT INTO user (user_id, user_name, user_pass, user_enabled_flag, user_last_org_id)'
        ' VALUES (?, ?, ?, ?, ?)',
        (user_id, 'test-user', generate_password_hash('test-user'), 1, org_id)
    )

    # Generate the organisation
    db.execute(
        'INSERT INTO organisation (org_id, org_name, org_enabled_flag) VALUES (?, ?, ?)',
        (org_id, 'TestCompany', 1)
    )

    # Add user access to the company
    db.execute(
        'INSERT INTO user_organisation (org_id_fk, user_id_fk) VALUES (?, ?)',
        (org_id, user_id)
    )

    # generate bank accounts

    accounts = [
        {
            'bank_id' : str(uuid4()),
            'bank_name': 'Current Account',
            'bank_reference': '00-00-00-00000000',
            'bank_created_date' : datetime.datetime.now().strftime('%Y-%m-%d'),
            'bank_enabled_flag' : 1,
            'bank_currency_code': 'gbp',
            'org_id_fk': org_id

        },
        {
            'bank_id': str(uuid4()),
            'bank_name': 'Savings Account',
            'bank_reference': '00-00-00-00000001',
            'bank_created_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'bank_enabled_flag': 1,
            'bank_currency_code': 'gbp',
            'org_id_fk': org_id

        },
        {
            'bank_id': str(uuid4()),
            'bank_name': 'ISA',
            'bank_reference': '00-00-00-00000002',
            'bank_created_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'bank_enabled_flag': 1,
            'bank_currency_code': 'gbp',
            'org_id_fk': org_id

        },
        {
            'bank_id': str(uuid4()),
            'bank_name': 'Disabled Account',
            'bank_reference': '00-00-00-00000003',
            'bank_created_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'bank_enabled_flag': 0,
            'bank_currency_code': 'gbp',
            'org_id_fk': org_id

        }
    ]

    for account in accounts:
        db.execute(
            'INSERT INTO bank (bank_id, bank_name, bank_reference, bank_created_date, bank_enabled_flag,'
            ' bank_currency_code, org_id_fk) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (account['bank_id'], account['bank_name'], account['bank_reference'], account['bank_created_date'],
             account['bank_enabled_flag'], account['bank_currency_code'], account['org_id_fk'], )
        )

    # generate categories

    income = db.execute(
        'SELECT cat_type_id FROM category_type WHERE cat_type_name=?',
        ('Income',)
    ).fetchone()

    income = income['cat_type_id']

    expense = db.execute(
        'SELECT cat_type_id FROM category_type WHERE cat_type_name=?',
        ('Expense',)
    ).fetchone()

    expense = expense['cat_type_id']

    categories = [
        {
            'category_id': str(uuid4()),
            'category_name': 'Salary',
            'category_enabled_flag': 1,
            'org_id_fk': org_id,
            'cat_type_id_fk': income
        },
        {
            'category_id': str(uuid4()),
            'category_name': 'Bonus',
            'category_enabled_flag': 1,
            'org_id_fk': org_id,
            'cat_type_id_fk': income
        },
        {
            'category_id': str(uuid4()),
            'category_name': 'Interest',
            'category_enabled_flag': 1,
            'org_id_fk': org_id,
            'cat_type_id_fk': income
        },
        {
            'category_id': str(uuid4()),
            'category_name': 'Mortgage',
            'category_enabled_flag': 1,
            'org_id_fk': org_id,
            'cat_type_id_fk': expense
        },
        {
            'category_id': str(uuid4()),
            'category_name': 'Phone',
            'category_enabled_flag': 1,
            'org_id_fk': org_id,
            'cat_type_id_fk': expense
        },
        {
            'category_id': str(uuid4()),
            'category_name': 'Food',
            'category_enabled_flag': 1,
            'org_id_fk': org_id,
            'cat_type_id_fk': expense
        },
        {
            'category_id': str(uuid4()),
            'category_name': 'Fuel',
            'category_enabled_flag': 1,
            'org_id_fk': org_id,
            'cat_type_id_fk': expense
        },
        {
            'category_id': str(uuid4()),
            'category_name': 'Coffee',
            'category_enabled_flag': 1,
            'org_id_fk': org_id,
            'cat_type_id_fk': expense
        },
        {
            'category_id': str(uuid4()),
            'category_name': 'Furniture',
            'category_enabled_flag': 1,
            'org_id_fk': org_id,
            'cat_type_id_fk': expense
        },
        {
            'category_id': str(uuid4()),
            'category_name': 'Socializing',
            'category_enabled_flag': 1,
            'org_id_fk': org_id,
            'cat_type_id_fk': expense
        },
        {
            'category_id': str(uuid4()),
            'category_name': 'Utilities',
            'category_enabled_flag': 1,
            'org_id_fk': org_id,
            'cat_type_id_fk': expense
        }
    ]

    for category in categories:
        db.execute(
            'INSERT INTO categories (category_id, category_name, category_enabled_flag, org_id_fk, cat_type_id_fk)'
            ' VALUES (?, ?, ?, ?, ?)',
            ( category['category_id'], category['category_name'], category['category_enabled_flag'],
              category['org_id_fk'], category['cat_type_id_fk'])
        )

    # generate transactions

    for i in range(1000):

        for account in accounts:

            for category in categories:

                delta = random.randrange(0, 500)
                trans_date = datetime.datetime.today() - datetime.timedelta(days=delta)
                trans_date = datetime.datetime.strftime(trans_date, '%Y-%m-%d')

                multiplier = random.randrange(10, 100)
                value = round( random.random() * multiplier)

                today = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')

                db.execute(
                    'INSERT INTO transactions'
                    ' (trans_id, trans_post_date, trans_created_date,'
                    ' trans_value, trans_description, user_id_fk,'
                    ' org_id_fk, bank_id_fk, category_id_fk)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (str(uuid4()), trans_date, today,
                     value, 'Test Transaction', user_id,
                     org_id, account['bank_id'], category['category_id'],)
                )

    db.commit()

    click.echo('Generated test data.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(generate_test_data)
