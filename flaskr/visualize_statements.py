from flask import (
    Blueprint, render_template, session, send_file
)
from flaskr.forms import VisuForm
import sys, os
from . import getter, diagrams

bp = Blueprint('visualise', __name__, url_prefix='')


def get_stats_visu():
    data = []
    session_ids = set()
    num_passed_exec = 0
    num_failed_exec = 0
    for s in session['statements']:
        current_id = getter.get_session_id(s)
        verb = getter.get_verb(s)
        activity = getter.get_activity(s)
        session_ids.add(current_id)
        if activity == 'a programming execution':
            if verb == 'passed':
                num_passed_exec += 1
            if verb == 'failed':
                num_failed_exec += 1
    data.append('<ul>')
    data.append('<li> Number of sessions: ' + str(len(session_ids)) + '</li>')
    data.append('<li> Number of passed executions: ' + str(num_passed_exec) + '</li>')
    data.append('<li> Number of failed executions: ' + str(num_failed_exec) + '</li>')
    data.append('</ul>')
    return data

def get_keywords_visu():
    data = []
    keywords = {}
    for s in session['statements']:
        if getter.is_keyword_statement(s):
            kw = getter.get_keyword(s)
            if kw not in keywords.keys():
                keywords[kw] = 1
            else:
                keywords[kw] += 1
    #data.append(keywords)
    return diagrams.image_circular_diagram(keywords)

def get_execution_visu():
    data = []
    ord_statements = {}
    filter_interactions = {('opened', 'application'), ('closed', 'application'), ('updated', 'student-number'), ('updated', 'partner-number'),
    ('switched', 'mode'), ('created', 'file'), ('opened', 'file'), ('saved-as', 'file'), ('saved', 'file'), ('copied', 'output-console')}
    
    for s in session['statements']:
        verb, id = getter.get_verb(s), getter.get_activity_parsed_id(s)
        session_id = getter.get_session_id(s)
        timestamp = getter.get_timestamp(s)
        if session_id not in ord_statements.keys():
            ord_statements[session_id] = {'timestamp': timestamp, 'statements': [s], 'nb_executions': 0, 'nb_instructions' : 0}
        else:
            ord_statements[session_id]['statements'].append(s)
        if verb == "started" and id == "execution":
            ord_statements[session_id]['nb_executions'] += 1
        elif verb == "modified" and id == "instruction":
            ord_statements[session_id]['nb_instructions'] += 1
    
    sorted_statements = sorted(ord_statements.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    for s in sorted_statements:
        nb_exec = str(s[1]['nb_executions'])
        nb_inst = str(s[1]['nb_instructions'])
        if nb_exec == '0':
            print("ZERO", file=sys.stdout)
            html_row = '<p style="color: red">'
        else:
            html_row = '<p>'
        html_row += '<b> Session timestamp :' + s[1]['timestamp'][0:19]  + ' | Nombre d\'execution  : ' + \
            nb_exec +  ' | Nombre modif. instructions  : ' + nb_inst  + ' | Session ID : ' + s[0] + '</b> </p>' 
        data.append(html_row)
    
    return data

def get_errors_visu():
    data = [0]
    errors= {}
    errors_verb_id = { ('received', 'execution-error'), ('received', 'execution-warning'), \
        ('received', 'evaluation-error'), ('received', 'evaluation-warning')}
    
    for s in session['statements']:
        verb, id = getter.get_verb(s), getter.get_activity_parsed_id(s)
        if (verb, id) in errors_verb_id:
            error = getter.get_error_first_group(s)
            if error not in errors.keys():
                errors[error] = 1
            else:
                errors[error] += 1
    return diagrams.image_circular_diagram(errors)


def get_instructions_visu():
    data = [0]
    instructions_type = {}
    
    for s in session['statements']:
        verb, id = getter.get_verb(s), getter.get_activity_parsed_id(s)
        if (verb, id)  == ('modified', 'instruction'):
            s_type = getter.get_instruction_type(s)
            if s_type not in instructions_type.keys():
                instructions_type[s_type] = 1
            else:
                instructions_type[s_type] += 1
    return diagrams.image_circular_diagram(instructions_type)

@bp.route('/visu', methods=('GET', 'POST'))
def register_visu():
    form = VisuForm()
    data = []
    display_page = getter.check_statements_existence()
    if display_page and form.validate_on_submit():
        if form.radio.data == 'stats':
            data = get_stats_visu()
        elif form.radio.data == 'keywords': # Image
            return get_keywords_visu()
        elif form.radio.data == 'execution':
            data = get_execution_visu()
        elif form.radio.data == 'errors': # Image
            return get_errors_visu()
        elif form.radio.data == 'instructions': # Image
            return get_instructions_visu()
    return render_template("visu.html", display_page=display_page, form=form, data=data)