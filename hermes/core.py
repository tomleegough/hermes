from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from hermes.auth import login_required
from hermes.auth import update_orgs
import hermes.core_queries as queries

bp = Blueprint('accounts', __name__)

##### Main route
@bp.route('/')
@login_required
def index():
    if 'current_org' not in session:
        flash('Select an organisation')

    values = queries.category_values_for_current_org()
    accounts = queries.get_bank_accounts_for_current_org()
    chart_data = queries.dashboard_graph()

    return render_template(
        'core/dashboard.html',
        categories=values,
        accounts=accounts,
        chart_data=chart_data
    )

@bp.route('/about')
def about():

    return render_template(
        'core/pages/about.html'
    )


@bp.route('/help')
def help():

    return render_template(
        'core/pages/help.html'
    )

##### Banking Core Module

@bp.route('/accounts')
@login_required
def show_accounts():
    accounts = queries.get_bank_accounts_for_current_org()
    return render_template(
        'core/cards/accounts.html',
        accounts=accounts
    )


@bp.route('/create/', methods=['POST', 'GET'])
@login_required
def create_account():

    if request.method == 'POST':
        queries.create_bank_account(request.form)
        return redirect(
            url_for('accounts.show_accounts')
        )

    return render_template(
        'core/forms/account.html',
        account=account,
        action='create'
    )


@bp.route('/edit/<bank_id>', methods=['POST', 'GET'])
@login_required
def account(bank_id):
    account = queries.get_bank_account(bank_id)

    if request.method == 'POST':
        queries.update_bank_details(request.form, bank_id)
        return redirect(
            url_for('accounts.show_accounts')
        )

    return render_template(
        'core/forms/account.html',
        account=account,
        action='edit'
    )

##### Transactions
@bp.route('/view/<category_id>/transactions')
@login_required
def view_transactions(category_id):

    transactions = queries.get_transactions_for_category(category_id)
    cat = queries.get_category_by_id(category_id)

    return render_template(
        'core/tables/transactions.html',
        transactions=transactions,
        category=cat
    )


@bp.route('/create/transaction/', methods=['POST', 'GET'])
@login_required
def create_transaction():
    categories = queries.get_active_categories_for_current_org()
    accounts = queries.get_bank_accounts_for_current_org()
    vat_codes = queries.get_vat_codes()

    if request.method == 'POST':
        queries.create_transaction(request.form)
        return redirect(
            url_for('accounts.show_accounts')
        )

    return render_template(
        'core/forms/transaction.html',
        action='create',
        categories=categories,
        accounts=accounts,
        vat_codes=vat_codes
    )

##### Settings

@bp.route('/categories')
@login_required
def show_categories():
    categories = queries.get_all_categories_for_org()
    return render_template(
        'core/tables/categories.html',
        categories=categories
    )


@bp.route('/feedback')
@login_required
def feedback():

    return render_template(
        'core/pages/feedback.html'
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
        return redirect(
            url_for('accounts.show_categories')
        )

    if item == 'organisations':
        queries.change_org_status(status_flag, id)
        return redirect(
            url_for('accounts.show_organisations')
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
                url_for('accounts.show_categories')
            )

        return render_template(
            'core/forms/add_edit_category.html',
            category='',
            cat_types= cat_types,
            action='Create'
        )

    if item == 'organisation':
        org_types = queries.get_organisation_types()

        if request.method == 'POST':
            queries.create_organisation(request.form)
            update_orgs()
            return redirect(
                url_for('accounts.show_organisations')
            )

        return render_template(
            'core/forms/add_edit_org.html',
            org_types= org_types,
            org='',
            action='Create'
        )


@bp.route('/category/<action>/<cat_id>', methods=['POST', 'GET'])
@login_required
def category(action, cat_id):

    if request.method == 'POST' and action == 'add':
        if 'active_flag' not in request.form:
            request.form['active_flag'] = 0
        queries.create_category(request.form)
        return redirect(
            url_for('accounts.show_categories')
        )

    if request.method == 'POST' and action == 'edit':
        if 'active_flag' not in request.form:
            request.form['active_flag'] = 0
        queries.update_category(request.form, cat_id)
        return redirect(
            url_for('accounts.show_categories')
        )

    cat_types = queries.get_category_types()
    category = queries.get_category_by_id(cat_id)

    return render_template(
        'core/forms/category.html',
        cat_types=cat_types,
        category=category,
        action=action
    )


##### Organisations
@bp.route('/organisations')
@login_required
def show_organisations():
    organisations = queries.get_all_orgs_for_current_user()
    return render_template(
        'core/tables/organisations.html',
        organisations=organisations
    )


@bp.route('/organisation/<action>/<org_id>', methods=['POST', 'GET'])
@login_required
def organisation(action, org_id):
    org = queries.get_org_by_id(org_id)
    org_types = queries.get_organisation_types()

    if request.method == 'POST' and action == 'edit':
        queries.update_organistation(request.form, org_id)
        update_orgs()
        return redirect(
            url_for('accounts.show_organisations')
        )

    return render_template(
        'core/forms/add_edit_org.html',
        org=org,
        action=action,
        org_types=org_types
    )


@bp.route('/organisation/<org_id>')
@login_required
def change_org(org_id):
    session['current_org'] = org_id
    org_data = queries.get_org_by_id(org_id)
    session['current_org_name'] = org_data['org_name']
    return redirect(
        url_for('accounts.index')
    )
