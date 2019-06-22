from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from uuid import uuid4

from hermes.auth import login_required
from hermes.db import get_db
from hermes.session import update_orgs

bp = Blueprint('settings', __name__, url_prefix='/settings')


@bp.route('/categories')
@login_required
def show_categories():
    db = get_db()
    categories = db.execute(
        'SELECT * FROM categories'
        ' JOIN category_type on cat_type_id = cat_type_id_fk'
        ' WHERE org_id_fk = ?',
        (session['current_org'],)
    ).fetchall()

    return render_template('tables/categories.html', categories=categories)


@bp.route('/<item>/change-status/<id>/<status_flag>')
def change_status(item, id, status_flag):
    if status_flag == '0':
        status_flag = 1
    if status_flag == '1':
        status_flag = 0

    db = get_db()

    if item == 'categories':
        db.execute(
            'UPDATE categories'
            ' SET category_enabled_flag = ? WHERE category_id = ?',
            (status_flag, id,)
        )
        url = url_for('settings.show_categories')

    if item == 'organisations':
        db.execute(
            'UPDATE organisation'
            ' SET org_enabled_flag = ? WHERE org_id = ?',
            (status_flag, id,)
        )
        update_orgs()
        url = url_for('settings.show_organisations')
        if id == session['current_org'] and status_flag == 0:
            session['current_org'] == ''

    db.commit()

    return redirect(url)


@bp.route('/categories/<action>/', defaults={'cat_id': ''}, methods=['POST', 'GET'])
@bp.route('/categories/<action>/<cat_id>', methods=['POST', 'GET'])
@login_required
def category(action, cat_id):
    db = get_db()

    if request.method == 'POST' and action == 'add':
        cat_id = str(uuid4())
        cat_name = request.form['cat_name']
        if 'active_flag' not in request.form:
            active_flag = 0
        else:
            active_flag = request.form['active_flag']
        type_id_fk = request.form['type_id']

        db.execute(
            'INSERT INTO categories ('
            ' category_id, category_name, category_enabled_flag,'
            ' org_id_fk, cat_type_id_fk)'
            ' VALUES (?, ?, ?, ?, ?)',
            (cat_id, cat_name, active_flag,
             session['current_org'], type_id_fk,)
        )

        db.commit()

        return redirect(url_for('settings.show_categories'))

    if request.method == 'POST' and action == 'edit':
        cat_name = request.form['cat_name']
        if 'active_flag' not in request.form:
            active_flag = 0
        else:
            active_flag = request.form['active_flag']
        type_id_fk = request.form['type_id']

        db.execute(
            'UPDATE categories'
            ' SET category_name = ?, category_enabled_flag =?, cat_type_id_fk =?'
            ' WHERE category_id = ?',
            (cat_name, active_flag, type_id_fk, cat_id,)
        )

        db.commit()

        return redirect(url_for('settings.show_categories'))

    cat_types = db.execute(
        'SELECT * FROM category_type'
    ).fetchall()

    category = db.execute(
        'SELECT * FROM categories WHERE category_id = ?',
        (cat_id,)
    ).fetchone()

    return render_template(
        'forms/category.html',
        cat_types=cat_types,
        category=category,
        action=action
    )

@bp.route('/organisations')
@login_required
def show_organisations():
    db = get_db()
    organisations = db.execute(
        'SELECT * FROM organisation'
        ' JOIN user_organisation on org_id = org_id_fk'
        ' WHERE user_id_fk = ?',
        (session['user_id'],)
    ).fetchall()

    return render_template('tables/organisations.html', organisations=organisations)


@bp.route('/organisations/<action>/', defaults={'org_id': ''}, methods=['POST', 'GET'])
@bp.route('/organisations/<action>/<org_id>', methods=['POST', 'GET'])
def organisation(action, org_id):
    db = get_db()

    if request.method == 'POST':
        org_name = request.form['org_name']
        if 'org_enabled_flag' not in request.form:
            org_enabled_flag = 0
        else:
            org_enabled_flag = request.form['org_enabled_flag']

    if request.method == 'POST' and action == 'add':
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

    if request.method == 'POST' and action == 'edit':
        db.execute(
            'UPDATE organisation'
            ' SET org_name =?, org_enabled_flag = ?'
            ' WHERE org_id = ?',
            (org_name, org_enabled_flag, org_id,)
        )

        db.commit()
        update_orgs()

        if org_id == session['current_org'] and org_enabled_flag == 0:
            session['current_org'] == ''

        return redirect(url_for('settings.show_organisations'))

    org = db.execute(
        'SELECT * FROM organisation WHERE org_id=?',
        (org_id,)
    ).fetchone()

    return render_template('forms/org.html', org=org, action=action)


@bp.route('/organisation/<return_url>/<org_id>')
def change_org(org_id, return_url):
    session['current_org'] = org_id
    if return_url == 'o':
        return redirect(url_for('settings.show_organisations'))
    else:
        return redirect(url_for('accounts.index'))
