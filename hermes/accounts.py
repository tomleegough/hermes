from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
)

from hermes.auth import login_required
import hermes.queries as queries

bp = Blueprint('accounts', __name__)


@bp.route('/')
@login_required
def index():
    if 'current_org' not in session:
        flash('Select an organisation')

    values = queries.category_values_for_current_org()
    accounts = queries.get_bank_accounts_for_current_org()
    chart_data = queries.dashboard_graph()

    return render_template(
        'dashboard.html',
        categories=values,
        accounts=accounts,
        chart_data=chart_data
    )
