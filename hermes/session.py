from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from hermes.db import get_db


def update_orgs():
    db = get_db()

    orgs = db.execute(
        'SELECT * FROM organisation'
        ' JOIN user_organisation on org_id = org_id_fk'
        ' WHERE user_id_fk = ? and org_enabled_flag = 1',
        (session['user_id'],)
    ).fetchall()

    session['orgs'] = []

    for org in orgs:
        session['orgs'].append({
            'org_id': org['org_id'],
            'org_name': org['org_name']
        })
