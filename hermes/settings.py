from flask import (
    Blueprint, redirect, render_template, request, url_for, session
)

from hermes.auth import login_required
from hermes.session import update_orgs
import hermes.queries as queries

bp = Blueprint('settings', __name__, url_prefix='/settings')


@bp.route('/categories')
@login_required
def show_categories():
    categories = queries.get_all_categories_for_org()
    return render_template(
        'tables/categories.html',
        categories=categories
    )


@bp.route('/<item>/change-status/<id>/<status_flag>')
@login_required
def change_status(item, id, status_flag):
    if status_flag == '0':
        status_flag = 1
    if status_flag == '1':
        status_flag = 0

    if item == 'categories':
        queries.change_category_status(status_flag, id)
        url = url_for('settings.show_categories')

    if item == 'organisations':
        queries.change_org_status(status_flag, id)
        update_orgs()
        url = url_for('settings.show_organisations')

    return redirect(
        url
    )



@bp.route('/<item>/create/', methods=['POST', 'GET'])
@login_required
def create_item(item):
    # TODO: Check that a site is selected before a category is created
    if item == 'category':
        cat_types = queries.get_category_types()

        if request.method == 'POST':
            if 'active_flag' not in request.form:
                request.form['active_flag'] = 0
            queries.create_category(request.form)
            return redirect(
                url_for('settings.show_categories')
            )

        return render_template(
            'forms/add_edit_category.html',
            category='',
            cat_types= cat_types,
            action='Create'
        )

    if item == 'organisation':
        if request.method == 'POST':
            queries.create_organisation(request.form)
            update_orgs()
            return redirect(
                url_for('settings.show_organisations')
            )

        return render_template(
            'forms/add_edit_org.html'
        )


@bp.route('/category/<action>/<cat_id>', methods=['POST', 'GET'])
@login_required
def category(action, cat_id):

    if request.method == 'POST' and action == 'add':
        if 'active_flag' not in request.form:
            request.form['active_flag'] = 0
        queries.create_category(request.form)
        return redirect(
            url_for('settings.show_categories')
        )

    if request.method == 'POST' and action == 'edit':
        if 'active_flag' not in request.form:
            request.form['active_flag'] = 0
        queries.update_category(request.form, cat_id)
        return redirect(
            url_for('settings.show_categories')
        )

    cat_types = queries.get_category_types()
    category = queries.get_category_by_id(cat_id)

    return render_template(
        'forms/category.html',
        cat_types=cat_types,
        category=category,
        action=action
    )

@bp.route('/organisations')
@login_required
def show_organisations():
    organisations = queries.get_all_orgs_for_current_user()
    return render_template(
        'tables/organisations.html',
        organisations=organisations
    )


@bp.route('/organisation/<action>/<org_id>', methods=['POST', 'GET'])
@login_required
def organisation(action, org_id):
    org = queries.get_org_by_id(org_id)

    if request.method == 'POST' and action == 'edit':
        queries.update_organistation(request.form, org_id)
        update_orgs()
        return redirect(
            url_for('settings.show_organisations')
        )

    return render_template(
        'forms/org.html',
        org=org,
        action=action
    )


@bp.route('/organisation/<org_id>')
@login_required
def change_org(org_id):
    session['current_org'] = org_id
    return redirect(
        url_for('accounts.index')
    )