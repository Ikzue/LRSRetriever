from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, session
)
from flaskr.forms import LogsForm
import requests, json, sys, datetime

bp = Blueprint('visualise', __name__, url_prefix='')

def statement_info_row(s):
    info = '<tr>'
    info += '<td>' + s['statement']['actor']['name'] + '</td>'
    info += '<td>' + s['statement']['verb']['display']['en-US'] + '</td>'
    info += '<td>' + s['statement']['object']['definition']['name']['en-US'] + '</td>'
    info += '<td>' + s['statement']['timestamp'][:19] + '</td>'
    info += "</tr>"
    return info

def statement_info(s):
    info = s['statement']['actor']['name']
    info += ' ' + s['statement']['verb']['display']['en-US']
    info += ' ' + s['statement']['object']['definition']['name']['en-US']
    return info

def get_chrono_logs():
    data = []
    data.append('<table>')
    data.append('<th scope="col">Name</th>\n<th scope="col">Verb</th>\n'\
        '<th scope="col">Activity</th>\n<th scope="col">Timestamp</th>')
    for s in session['statements']:
        data.append(statement_info_row(s))
    data.append('</table>')
    return data

def get_session_logs():
    data = []
    ord_statements = {}
    for s in session['statements']:
        session_id = s['statement']['context']['extensions']['https://www.lip6.fr/mocah/invalidURI/extensions/session-id']
        timestamp = s['statement']['timestamp']
        #print(timestamp, file=sys.stdout)
        if session_id not in ord_statements.keys():
            ord_statements[session_id] = {'timestamp': timestamp, 'statements': [s]}
        else:
            ord_statements[session_id]['statements'].append(s)
    
    sorted_statements = sorted(ord_statements.items(), key=lambda x: x[1]['timestamp'])
    for s in sorted_statements:
        data.append('<p><b> Session timestamp :' + s[1]['timestamp'][0:19] + ' Session ID:' + s[0] + '</b><br>')
        for s2 in s[1]['statements']:
            data.append(statement_info(s2))
            data.append('<br>')
        data.append('</p>')
    
    return data



@bp.route('/logs', methods=('GET', 'POST'))
def register_logs():
    form = LogsForm()
    data = []
    display_page = True
    if 'statements' not in session.keys() or len(session['statements']) == 0:
        display_page=False
    elif form.validate_on_submit():
        if form.radio.data == 'chrono':
            data = get_chrono_logs()
        elif form.radio.data == 'session':
            data = get_session_logs()
        elif form.radio.data == 'etudiant':
            pass
    return render_template("logs.html", display_page=display_page, form=form, data=data)


@bp.route('/visu', methods=('GET', 'POST'))
def register_visu():
    return render_template("base.html")




@bp.route('/analyses', methods=('GET', 'POST'))
def register_analysis():
    return render_template("base.html")

