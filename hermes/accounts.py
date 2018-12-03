from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from uuid import uuid4

from hermes.auth import login_required
from hermes.db import get_db
from hermes.session import update_orgs

bp = Blueprint('accounts', __name__)


@bp.route('/')
@login_required
def index():
    if 'current_org' not in session:
        flash('Select an organisation')
    return render_template('dashboard.html')


@bp.route('/organisation/create', methods=['GET', 'POST'])
def create_organisation():
    if request.method == 'POST':
        org_name = request.form['org_name']
        if 'org_enabled_flag' not in request.form:
            org_enabled_flag = 0
        else:
            org_enabled_flag = request.form['org_enabled_flag']

        db = get_db()

        org_id = str(uuid4())

        db.execute(
            'INSERT INTO organisation (org_id, org_name, org_enabled_flag)'
            ' VALUES (?, ?, ?)',
            (org_id, org_name, org_enabled_flag)
        )

        db.execute(
            'INSERT INTO user_organisation (user_id_fk, org_id_fk)'
            ' VALUES (?,?)',
            (g.user['user_id'], org_id)
        )

        db.commit()

        update_orgs()

        return redirect(url_for('accounts.index'))

    return render_template('forms/add_edit_org.html')


@bp.route('/organisation/<org_id>')
def change_org(org_id):
    session['current_org'] = org_id
    return redirect(url_for('accounts.index'))
