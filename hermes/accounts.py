from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from uuid import uuid4

from hermes.auth import login_required
from hermes.db import get_db
from hermes.banking import bank_values

bp = Blueprint('accounts', __name__)


@bp.route('/')
@login_required
def index():
    if 'current_org' not in session:
        flash('Select an organisation')

    values = category_values()
    accounts = bank_values()

    return render_template(
        'dashboard.html',
        categories=values,
        accounts=accounts
    )


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
        ' GROUP BY category_id',
        (session['current_org'],)
    ).fetchall()

    return values
