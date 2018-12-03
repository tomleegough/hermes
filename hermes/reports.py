from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import uuid

from hermes.auth import login_required
from hermes.db import get_db

bp = Blueprint('reports', __name__)


@bp.route('/reports')
@login_required
def reports():
    return render_template('reports/reports.html')


@bp.route('/reports/income-statement')
@login_required
def income():

    db = get_db()

    accounts = db.execute(
        'SELECT type_name, accounts_name, accounts_code, sum(splits_value)'
        ' FROM splits'
        ' JOIN transactions on trans_id = trans_id_fk'
        ' JOIN accounts on accounts_id = accounts_id_fk'
        ' JOIN type on type_id = type_id_fk'
        ' WHERE type_report = "income"'
        ' GROUP BY type_name, accounts_code'
        ' ORDER BY accounts_code'
    ).fetchall()

    total = 0

    for each in accounts:
        total += each['sum(splits_value)']

    return render_template('reports/income.html', accounts=accounts, total=total)


@bp.route('/reports/balance-sheet')
@login_required
def balance():
    return render_template('reports/balance.html')
