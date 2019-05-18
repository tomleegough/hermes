from flask import (
    Blueprint, redirect, render_template, request, url_for
)


from hermes.auth import login_required
import hermes.queries as queries

bp = Blueprint('bank', __name__, url_prefix='/bank')


@bp.route('/accounts')
@login_required
def show_accounts():
    accounts = queries.bank_values()
    return render_template(
        'cards/accounts.html',
        accounts=accounts
    )


@bp.route('/create/', methods=['POST', 'GET'])
@login_required
def create_account():

    if request.method == 'POST':
        queries.create_bank_account(request.form)
        return redirect(
            url_for('bank.show_accounts')
        )

    return render_template(
        'forms/account.html',
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
            url_for('bank.show_accounts')
        )

    return render_template(
        'forms/account.html',
        account=account,
        action='edit'
    )


@bp.route('/create/transaction/', methods=['POST', 'GET'])
@login_required
def create_transaction():
    categories = queries.get_active_categories_for_current_org()
    accounts = queries.get_bank_accounts_for_current_org()

    if request.method == 'POST':
        queries.create_transaction(request.form)
        return redirect(
            url_for('bank.show_accounts')
        )

    return render_template(
        'forms/transaction.html',
        action='create',
        categories=categories,
        accounts=accounts
    )


@bp.route('/transaction/<action>/<bank_id>/', methods=['POST', 'GET'])
@login_required
def transaction(action, bank_id):

    categories = queries.get_active_categories_for_current_org()

    if action == 'add':
        if bank_id == '':
            accounts = queries.get_bank_accounts_for_current_org()

        if request.method == 'POST':
            queries.create_transaction(request.form)
            return redirect(
                url_for('bank.show_accounts')
            )

        return render_template(
            'forms/transaction.html',
            action=action,
            categories=categories,
            accounts=accounts,
            bank_id=bank_id
        )
