from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from uuid import uuid4

from hermes.auth import login_required
from hermes.db import get_db
from hermes.banking import bank_values

import hermes.queries as queries

bp = Blueprint('accounts', __name__)


@bp.route('/')
@login_required
def index():
    if 'current_org' not in session:
        flash('Select an organisation')

    values = queries.category_values()
    accounts = bank_values()

    return render_template(
        'dashboard.html',
        categories=values,
        accounts=accounts
    )
