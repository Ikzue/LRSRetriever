from flask import (
    Blueprint, render_template, session
)
from flaskr.forms import LogsForm
import sys, hashlib
from . import getter


filter_interaction = {('opened', 'application'), ('closed', 'application'), ('initialized', 'student-number'), ('initialized', 'partner-number'), 
('updated', 'student-number'), ('updated', 'partner-number'), ('switched', 'mode'), ('switched', 'file'), ('created', 'file'), 
('opened', 'file'), ('closed', 'file'), ('saved-as', 'file'), ('saved', 'file'), ('copied', 'output-console')}

# Interpretation ID doesn't exist anymore, and is now called 'evaluation'
filter_execution = {('started', 'execution'), ('passed', 'execution'), ('failed', 'execution'), ('terminated', 'execution'),
('started', 'evaluation'), ('passed', 'evaluation'), ('failed', 'evaluation'), ('terminated', 'evaluation'),
('started', 'interpretation'), ('passed', 'interpretation'), ('failed', 'interpretation')} 

filter_errors = {('received', 'evaluation-error'), ('received', 'evaluation-warning'), 
('received', 'execution-error'), ('received', 'execution-warning')}

filter_states = {('entered', 'typing-state'), ('entered', 'interacting-state'), ('entered', 'idle-state')}

filter_editor = {('typed', 'keyword'), ('modified', 'instruction'), ('deleted', 'text'), ('inserted', 'text'), 
('copied', 'text'), ('undid', 'sequence'), ('redid', 'sequence')}

bp = Blueprint('logs', __name__, url_prefix='')

def get_hashes(number_list, hash_list):
    hashes = []
    # Convert and get all student numbers
    number_list = number_list.split(';')
    for number in number_list:
        if number != '':
            my_hash = hashlib.sha1(str.encode(number))
            my_hash = my_hash.hexdigest()[:10]
            hashes.append(my_hash)
            

    # Get all hashes
    hash_list = hash_list.split(';')
    for my_hash in hash_list:
        if my_hash != '':
            hashes.append(my_hash)

    print(hashes)
    return hashes

def get_session_ids(session_ids):
    ids = []
    session_ids = session_ids.split(';')
    for s in session_ids:
        if s != '':
            ids.append(s)
    print(ids)
    return ids

def is_filtered(s, shown_data):
    verb, id = getter.get_verb(s), getter.get_activity_parsed_id(s)
    if not shown_data['interaction'] and (verb, id) in filter_interaction:
        return True
    elif not shown_data['execution'] and (verb, id) in filter_execution:
        return True
    elif not shown_data['errors'] and (verb, id) in filter_errors:
        return True
    elif not shown_data['states'] and (verb, id) in filter_states:
        return True
    elif not shown_data['editor'] and (verb, id) in filter_editor:
        return True

    if shown_data['hashes']:
        filter_statement = True
        actor_name = getter.get_actor_name(s)
        for student_hash in shown_data['hashes']:
            if student_hash in actor_name:
                filter_statement = False
        if filter_statement:
            return True

    if shown_data['session-ids']:
        filter_statement = True
        statement_session_id = getter.get_session_id(s)
        for session_id in shown_data['session-ids']:
            if session_id in statement_session_id:
                filter_statement = False
        if filter_statement:
            return True
    return False
    
    

def get_chrono_logs(shown_data):
    show_extensions = shown_data['extensions']
    data = []
    data.append('<table>')
    head_row = '<th scope="col">Name</th>\n<th scope="col">Verb</th>\n'\
        '<th scope="col">Activity</th>\n<th scope="col">Timestamp</th>'
    if show_extensions:
        head_row += '\n<th scope="col">Extensions</th>'
    data.append(head_row)
    for i in range(len(session['statements']), 0, -1):
        s = session['statements'][i-1]
        if not is_filtered(s, shown_data):
            data.append(getter.statement_HTML_table_row(s, show_extensions))
    data.append('</table>')
    return data

def get_session_logs(shown_data):
    show_extensions = shown_data['extensions']
    data = []
    ord_statements = {}
    
    for s in session['statements']:
        if not is_filtered(s, shown_data):
            session_id = getter.get_session_id(s)
            timestamp = getter.get_timestamp(s)
            #print(timestamp, file=sys.stdout)
            #print(timestamp, file=sys.stdout)
            if session_id not in ord_statements.keys():
                ord_statements[session_id] = {'timestamp': timestamp, 'statements': [s]}
            else:
                ord_statements[session_id]['statements'].append(s)
    
    sorted_statements = sorted(ord_statements.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    for s in sorted_statements:
        data.append('<p><b> Session timestamp :' + s[1]['timestamp'][0:19] + ' Session ID:' + s[0] + '</b><br>')
        s[1]['statements'].reverse()
        for s2 in s[1]['statements']:
            data.append(getter.statement_info(s2, show_extensions))
            data.append(s2['timestamp'] + '<br>')
        data.append('</p>')
    
    return data



@bp.route('/logs', methods=('GET', 'POST'))
def register_logs():
    form = LogsForm()
    data = []
    display_page = getter.check_statements_existence()
    if display_page and form.validate_on_submit():
        hashes = get_hashes(form.number_list.data, form.hash_list.data)
        session_ids = get_session_ids(form.session_id.data)
        shown_data = {'interaction': form.interaction.data, 'execution': form.execution.data, 'errors': form.errors.data, 
        'states': form.states.data, 'editor': form.editor.data, 'extensions': form.extensions.data, 'hashes':hashes, 'session-ids' : session_ids}
        if form.radio.data == 'chrono':
            data = get_chrono_logs(shown_data)
        elif form.radio.data == 'session':
            data = get_session_logs(shown_data)
    return render_template("logs.html", display_page=display_page, form=form, data=data)
