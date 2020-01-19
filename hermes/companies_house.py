from flask import (
    Blueprint, render_template
)

import requests

from hermes.auth import (
    login_required
)
import hermes.core_queries as queries

bp = Blueprint('companies_house', __name__)


@bp.route('/companies_house/<org_no>')
@login_required
def get_companies_house_data(org_no):
    api_key = queries.get_current_global_settings()
    api_key = api_key["companies_house_api_key"]

    url = 'https://api.companieshouse.gov.uk/company/'
    headers = {
        'Authorization': api_key
    }

    company_data = requests.get(
        url + org_no,
        headers= headers
    )

    officers = requests.get(
        url + org_no + '/officers',
        headers= headers
    )

    accounts = requests.get(
        url + org_no + '/filing-history?category=accounts',
        headers= headers
    )

    conf_statement = requests.get(
        url + org_no + '/filing-history?category=confirmation-statement',
        headers=headers
    )

    return render_template(
        'modules/companies_house.html',
        company_data=company_data.json(),
        officers= officers.json(),
        accounts= accounts.json(),
        conf_statement= conf_statement.json()
    )