from flask import (
    Blueprint, redirect, render_template, request, url_for
)


from hermes.auth import login_required
import hermes.queries as queries

bp = Blueprint('banking', __name__, url_prefix='/bank')


@bp.route('/')
def show_accounts():
    accounts = bank_values()
    return render_template(
        'cards/accounts.html',
        accounts=accounts
    )


@bp.route('/<action>/', defaults={'bank_id': ''}, methods=['POST', 'GET'])
@bp.route('/<action>/<bank_id>', methods=['POST', 'GET'])
@login_required
def account(action, bank_id):

    if request.method == 'POST' and action == 'add':
        queries.create_bank_account(request.form)
        return redirect(
            url_for('banking.show_accounts')
        )

    if request.method == 'POST' and action == 'edit':
        queries.update_bank_details(request.form, bank_id)
        return redirect(
            url_for('banking.show_accounts')
        )

    account = queries.get_bank_account(bank_id)

    return render_template(
        'forms/account.html',
        account=account,
        action=action
    )


@bp.route('/transaction/<action>/', defaults={'bank_id': ''}, methods=['POST', 'GET'])
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
                url_for('banking.show_accounts')
            )

        return render_template(
            'forms/transaction.html',
            action=action,
            categories=categories,
            accounts=accounts,
            bank_id=bank_id
        )
