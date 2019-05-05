from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from hermes.db import get_db

bp = Blueprint('queries', __name__)

# Accounts

## Sum transactions for each category

def category_values():
    db = get_db()

    values = db.execute(
        'SELECT *, '
        ' CASE WHEN sum(trans_value) is Null'
        '  THEN 0'
        '  ELSE sum(trans_value)'
        '  END AS "value"'
        ' FROM categories'
        ' LEFT JOIN transactions on category_id_fk = category_id'
        ' WHERE categories.org_id_fk = ?'
        ' GROUP BY category_id'
        ' ORDER BY value DESC',
        (session['current_org'],)
    ).fetchall()

    return values

def get_transactions_for_category(category):
    db = get_db()

    transactions = db.execute(
        'SELECT * FROM transactions WHERE org_id_fk = ? and caegory_if_fk = ?',
        (session['current_org'], category)
    ).fetchall()

    return transactions