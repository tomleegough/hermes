from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import hermes.queries as queries

def update_orgs():
    orgs = queries.get_active_orgs_for_current_user()

    session['orgs'] = []

    for org in orgs:
        session['orgs'].append(
            {
                'org_id': org['org_id'],
                'org_name': org['org_name']
            }
        )
