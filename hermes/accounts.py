from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
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

    return render_template(
        'dashboard.html',
        categories=values,
        accounts=accounts
    )
