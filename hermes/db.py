import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

from werkzeug.security import check_password_hash, generate_password_hash

from uuid import uuid4

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


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
