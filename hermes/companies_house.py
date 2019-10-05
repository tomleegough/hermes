from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

import requests

from hermes.auth import (
    login_required, group_admin
)
import hermes.core_queries as queries
import json

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

    response = requests.get(
        url + org_no,
        headers=headers
    )

    company_data = response.json()

    response = requests.get(
        url + org_no + '/officers',
        headers=headers
    )

    officers = response.json()

    return render_template(
        'modules/companies_house.html',
        company_data=company_data,
        officers= officers
    )