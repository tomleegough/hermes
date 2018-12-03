from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from uuid import uuid4

from hermes.auth import login_required
from hermes.db import get_db

bp = Blueprint('settings', __name__)


@bp.route('/settings/categories')
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


@bp.route('/settings/categories/change-status/<cat_id>/<status_flag>')
def category_change_status(cat_id, status_flag):

    if status_flag == '0':
        status_flag = 1
    if status_flag == '1':
        status_flag = 0

    db = get_db()
    db.execute(
        'UPDATE categories'
        ' SET category_enabled_flag = ? WHERE category_id = ?',
        (status_flag, cat_id,)
    )

    db.commit()

    return redirect(url_for('settings.show_categories'))


@bp.route('/settings/categories/<action>/', defaults={'cat_id': ''})
@bp.route('/settings/categories/<action>/<cat_id>', methods=['POST', 'GET'])
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
        'forms/add_edit_category.html',
        cat_types=cat_types,
        category=category,
        action=action
    )
