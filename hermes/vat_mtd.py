from flask import (
    Blueprint, render_template, flash, url_for, redirect, request, session
)

import requests

from hermes.auth import (
    login_required
)
import hermes.core_queries as queries
from hermes.db import get_db

bp = Blueprint('vat_mtd', __name__)


def get_mtd_headers():
    db = get_db()

    global_settings = db.execute(
        'SELECT * FROM global_settings'
    ).fetchone()

    headers = {
        'Accept': 'application/vnd.hmrc.1.0+json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + global_settings['mtd_server_token'],
        # Fraud Prevention Headers
        ## TODO:Complete the fraud prevention headers from HMRC https://developer.service.hmrc.gov.uk/api-documentation/docs/fraud-prevention
        'Gov-Client-Connection-Method': 'DESKTOP_APP_VIA_SERVER',
        'Gov-Client-Public-IP': request.remote_addr,
        'Gov-Client-Public-Port': '', #request.remote_port,
        'Gov-Client-Device-ID': '',
        'Gov-Client-User-IDs': '',
        'Gov-Client-Timezone': '',
        'Gov-Client-Local-IPs': '',
        'Gov-Client-Screens': '',
        'Gov-Client-Window-Size': '',
        'Gov-Client-Browser-Plugins': '',
        'Gov-Client-Browser-JS-User-Agent': '',
        'Gov-Client-Browser-Do-Not-Track': '',
        'Gov-Client-Multi-Factor': '',
        'Gov-Vendor-Version': '',
        'Gov-Vendor-Licence-IDs': '',
        'Gov-Vendor-Public-IPs': '',
        'Gov-Vendor-Forwarded': ''
    }

    return headers


@bp.route('/vat')
@login_required
def vat_index():
    return render_template(
        'modules/vat/index.html'
    )


@bp.route('/vat/hello/<end_point>')
@login_required
def hello_world(end_point):
    db = get_db()

    global_settings = db.execute(
        'SELECT * FROM global_settings'
    ).fetchone()

    hmrc_url = 'https://test-api.service.hmrc.gov.uk'

    headers = get_mtd_headers()

    if end_point == 'world':
        r = requests.get(
            hmrc_url + '/hello/world',
            headers=headers
        )
    elif end_point == 'user':
        auth_params = {
            'response_type': 'code',
            'client_id': global_settings['mtd_client_id'],
            'scope': 'hello',
            'redirect_url': request.url_root + 'vat/authorisation',
            'state': str( hash(session['id']) )
        }
        hmrc_auth_url = hmrc_url + '/oauth/authorize?'
        auth_params = 'response_type=%s&client_id=%s&scope=%s&state=%s&redirect_uri=%s' % (
            auth_params['response_type'],
            auth_params['client_id'],
            auth_params['scope'],
            auth_params['state'],
            auth_params['redirect_url']
        )
        endpoint = hmrc_auth_url + auth_params
        return redirect(endpoint)
    elif end_point == 'application':
        r = requests.get(
            hmrc_url + '/hello/application',
            headers=headers
        )
    else:
        flash('Error. Endpoint not valid')


    return render_template(
        'modules/vat/index.html',
        response=r.json()
    )

@bp.route('/vat/authorisation')
def token_exchange():

    db = get_db()

    global_settings = db.execute(
        'SELECT * FROM global_settings'
    ).fetchone()

    headers = get_mtd_headers()

    if global_settings['mtd_prod_status'] == 'on':
        base_url = 'https://api.service.hmrc.gov.uk'

    else:
        base_url = 'https://test-api.service.hmrc.gov.uk'

    payload = {
        'client_secret': global_settings['mtd_client_secrets'],
        'client_id': global_settings['mtd_client_id'],
        'grant_type': 'authorization_code',
        'redirect_uri': request.url_root + 'vat/authorisation',
        'code': request.args.get('code')
    }
    r = requests.post(
        base_url + '/oauth/token',
        json=payload,
        headers=headers
    )

    response = r.json()
    headers['Authorization'] = 'Bearer ' + response['access_token']

    r = requests.get(
        base_url + '/hello/user',
        json=payload,
        headers=headers
    )

    return render_template(
        'modules/vat/index.html',
        response=r.json()
    )