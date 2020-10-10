from flask import session
from hermes import core_queries as queries
import datetime


def test_dashboard(client, auth):
    auth.login()
    response = client.get('/')
    assert response.status_code == 200
    with client:
        assert b'Dashboard' in response.data


def test_static_pages(client, auth):
    for page in ['about', 'licence', 'help', 'feedback']:
        response = client.get('/' + page)
        assert response.status_code == 200
        assert page.title() in str(response.data)

    with client:
        auth.login()
        for page in ['about', 'licence', 'help', 'feedback']:
            response = client.get('/' + page)
            assert response.status_code == 200
            assert page.title() in str(response.data)


def test_show_bank_accounts(client, auth):
    url = '/accounts'
    response = client.get(url)
    assert response.status_code == 302
    with client:
        auth.login()
        response = client.get(url)
        assert response.status_code == 200
        assert b'accounts' in response.data


def test_sales_dash(client, auth):
    url = '/sales'
    assert client.get(url).status_code == 302
    with client:
        auth.login()
        response = client.get(url)
        assert response.status_code == 200
        assert b'Sales' in response.data


def test_purchases_dash(client, auth):
    url = '/purchases'
    assert client.get(url).status_code == 302
    with client:
        auth.login()
        response = client.get(url)
        assert response.status_code == 200
        assert b'Purchases' in response.data


def test_contacts_dash(client, auth):
    url = '/contacts'
    assert client.get(url).status_code == 302
    with client:
        auth.login()
        response = client.get(url)
        assert response.status_code == 200
        assert b'Contacts' in response.data


def test_show_accounts(client, auth):
    url = '/accounts'
    assert client.get(url).status_code == 302
    with client:
        auth.login()
        assert client.get(url).status_code == 200


def test_create_organisation(client, auth):
    url = '/organisation/create'
    assert client.get(url).status_code == 302
    with client:
        auth.login()
        assert client.get(url).status_code == 200
        org_types = queries.get_organisation_types()
        for org_type in org_types:
            client.post(
                '/organisation/create',
                data={
                    'org_name': org_type['org_type_name'],
                    'org_type': org_type['org_type_id'],
                    'org_enabled_flag': 1,
                    'org_no': '12345678',
                    'org_vat_flag': 1,
                    'org_vat': 123345
                }
            )


def test_orgs_in_session_org_list(client, auth):
    assert client.get('/').status_code == 302
    with client:
        auth.login()
        assert client.get('/').status_code == 200
        orgs = queries.get_active_orgs_for_current_user()
        for org in orgs:
            assert org['org_id'] in session['orgs']


def test_change_user_orgs(client, auth):
    assert client.get('/').status_code == 302
    with client:
        auth.login()
        assert client.get('/').status_code == 200
        orgs = queries.get_active_orgs_for_current_user()
        for org in orgs:
            client.get('/organisation/change/' + org['org_id'])
            assert org['org_name'] in client.get('/').data
            assert org['org_name'] in client.get('/organisations').data


def test_create_contact(client, auth):
    assert client.get('/').status_code == 302
    with client:
        auth.login()
        assert client.get('/contacts/create').status_code == 200
        client.get('/organisation/change/test_org_1')
        client.post(
            '/contacts/create',
            data={
                'contact_name': 'Tom Lee-Gough',
                'contact_account_no': '123456',
                'contact_foreign_account_no': '098987F',
                'contact_vat_registration': '234 567 899',
                'contact_company_no': '0099234',
                'contact_type': 'Company',
                'contact_email': 'tom@huginn.uk',
                'contact_phone': '09876555666',
                'contact_main_contact': 'Tom',
                'contact_web_address': 'www.tom.com'
            }
        )
        assert b'Tom Lee-Gough' in client.get('/contacts').data


def test_create_account(client, auth):
    url = '/create'
    assert client.get(url).status_code == 302
    with client:
        auth.login()
        for test in ['no_org_selected', 'org_selected']:
            if test == 'org_selected':
                client.get('/organisation/change/test_org_1')
                response = client.get(url)
                assert response.status_code == 200
            for bank_enabled_flag in [0, 1]:
                for bank_currency_code in ['gbp', 'usd', 'eur']:
                    for days in [-10, 0, 10]:
                        open_date = datetime.datetime.now() + datetime.timedelta(days=days)
                        open_date = open_date.strftime('%Y-%m-%d')
                        for open_balance in [-10, 0, 10]:
                            bank_name = '_'.join([
                                str(bank_enabled_flag),
                                bank_currency_code,
                                open_date,
                                str(open_balance)
                            ])
                        client.post(
                            url,
                            data={
                                'bank_name': bank_name,
                                'bank_reference': bank_name,
                                'bank_enabled_flag': bank_enabled_flag,
                                'bank_currency_code': bank_currency_code,
                                'open_date': open_date,
                                'open_balance': open_balance

                            }
                        )
                        if test == 'no_org_selected':
                            assert bank_name not in str(client.get('/').data)
                        else:
                            if bank_enabled_flag == 1:
                                assert bank_name in str(client.get('/').data)
                            assert bank_name in str(client.get('/accounts').data)


def test_edit_account(client, auth):
    with client:
        auth.login()
        accounts = queries.get_bank_accounts_for_current_org()
        for bank_id in accounts:
            url = '/edit/' + bank_id['bank_id']
            client.get(url)
            client.post(
                url,
                data={
                    'bank_name': bank_id['bank_name'] + '_edited',
                    'bank_reference': bank_id['bank_reference'] + '_edited',
                    'bank_enabled_flag': bank_id['bank_endabled_flag'],
                    'bank_currency_code': bank_id['bank_currency_code']
                }
            )
            response = client.get('/accounts')
            assert bank_id in response.data
            assert b'_edited' in response.data


def test_create_transactions(client, auth):
    url = '/create/transaction/'
    assert client.get(url).status_code == 302
    with client:
        auth.login()
        organisations = queries.get_all_orgs_for_current_user()
        for org in organisations:
            client.get('/organisation/change/' + org['org_id'])
            response = client.get(url)
            assert response.status_code == 200
            assert b'create Bank Transaction' in response.data
            categories = queries.get_active_categories_for_current_org()
            accounts = queries.get_bank_accounts_for_current_org()
            vat_codes = queries.get_vat_codes()
            trans_desc_n = -1
            for category in categories:
                for account in accounts:
                    for vat_code in vat_codes:
                        for day in [-1, 0, 1]:
                            for sign in [-1, 1]:
                                for value in [-100, 0, 100]:
                                    trans_desc_n += 1
                                    trans_desc = 'test_transaction_#' + str(trans_desc_n)
                                    client.post(
                                        url,
                                        data={
                                            'trans_date': datetime.datetime.now() + datetime.timedelta(days=day),
                                            'trans_value_net': value,
                                            'trans_value_vat': round(value/5, 2),
                                            'sign': sign,
                                            'trans_desc': trans_desc,
                                            'bank_id': account['bank_id'],
                                            'cat_id': category['cat_id'],
                                            'vat_type_id_fk': vat_code['vat_id']
                                        }
                                    )
                    response = client.get('/view/' + category['cat_id'] + '/transactions')
                    assert response.status_code == 200


def test_change_org_status(auth, client):
    url = '/organisation/change_status/'
    with client:
        auth.login()
        organisations = queries.get_all_orgs_for_current_user()
        for org in organisations:
            client.get(url + org['org_id'])
            with app.app_context():
                assert get_db().execute(
                    "select org_enabled_flag from org where org_id = '?'", org['org_id']
                ).fetchone() != org['org_enabled_flag']
