# The "Logs" webpage used to get logs from the retrieved statements.
from flask import (
    Blueprint, render_template, session
)
from flaskr.forms import LogsForm
from . import getter
from datetime import datetime, timedelta

# Separate the xAPI statements in different categories in order to show only the desired categories
filter_interaction = {('opened', 'application'), ('closed', 'application'), ('initialized', 'student-number'), ('initialized', 'partner-number'), 
('updated', 'student-number'), ('updated', 'partner-number'), ('switched', 'mode'), ('switched', 'file'), ('created', 'file'), 
('opened', 'file'), ('closed', 'file'), ('saved-as', 'file'), ('saved', 'file'), ('copied', 'output-console')}

# Interpretation ID doesn't exist anymore, and is now called 'evaluation'. 
# Use cases with 'interpretation' should be removed whenever the old statements are removed from the LRS's database.
filter_execution = {('started', 'execution'), ('passed', 'execution'), ('failed', 'execution'), ('terminated', 'execution'),
('started', 'evaluation'), ('passed', 'evaluation'), ('failed', 'evaluation'), ('terminated', 'evaluation'),
('started', 'interpretation'), ('passed', 'interpretation'), ('failed', 'interpretation')} 

filter_errors = {('received', 'evaluation-error'), ('received', 'evaluation-warning'), 
('received', 'execution-error'), ('received', 'execution-warning')}

filter_states = {('entered', 'typing-state'), ('entered', 'interacting-state'), ('entered', 'idle-state')}

filter_editor = {('typed', 'keyword'), ('modified', 'instruction'), ('deleted', 'text'), ('inserted', 'text'), 
('copied', 'text'), ('undid', 'sequence'), ('redid', 'sequence')}

bp = Blueprint('logs', __name__, url_prefix='')


def is_filtered(s, shown_data):
    # Filter a statement if the statement's category hasn't been selected
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

    return getter.filter_statement_hashes_id(s, shown_data['hashes'], shown_data['session-ids'])
    

def get_chrono_logs(shown_data):
    # Show logs in a reverse chronological order
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
    # Show logs in separate sessions, in a reverse chronological order according to the sessions' beginning times
    show_extensions = shown_data['extensions']
    data = []
    ord_statements = {}
    
    # Separate the statements in different sessions in the dictionnary ord_statements. 
    for s in session['statements']:
        if not is_filtered(s, shown_data):
            session_id = getter.get_session_id(s)
            timestamp = getter.get_timestamp(s)
            if session_id not in ord_statements.keys():
                ord_statements[session_id] = {'timestamp': timestamp, 'statements': [s], 'session_length' : 0}
            else:
                ord_statements[session_id]['statements'].append(s)
                first_timestamp = datetime.strptime(ord_statements[session_id]['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
                new_timestamp = datetime.strptime(getter.get_timestamp(s), '%Y-%m-%dT%H:%M:%S.%fZ')
                delta = new_timestamp - first_timestamp
                delta = delta.total_seconds()
                if delta > ord_statements[session_id]['session_length']:
                    ord_statements[session_id]['session_length'] = delta
    # Sort in reverse chronolgical order
    sorted_statements = sorted(ord_statements.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    for s in sorted_statements:
        data.append('<p><b> Session timestamp : ' + s[1]['timestamp'][0:19] + " Length : " +  str(s[1]['session_length']) +
         's Session ID:' + s[0] + '</b><br>')
        s[1]['statements'].reverse()
        for s2 in s[1]['statements']:
            data.append(getter.statement_info(s2, show_extensions))
            data.append(s2['timestamp'] + '<br>')
        data.append('</p>')
    
    return data



@bp.route('/logs', methods=('GET', 'POST'))
def register_logs():
    #Show the webpage and the logs form
    form = LogsForm()
    data = []
    display_page = getter.statements_in_session()
    if display_page and form.validate_on_submit():
        hashes = getter.get_hashes(form.number_list.data, form.hash_list.data)
        session_ids = getter.get_session_ids(form.session_id.data)
        shown_data = {'interaction': form.interaction.data, 'execution': form.execution.data, 'errors': form.errors.data, 
        'states': form.states.data, 'editor': form.editor.data, 'extensions': form.extensions.data, 'hashes':hashes, 'session-ids' : session_ids}
        if form.radio.data == 'chrono':
            data = get_chrono_logs(shown_data)
        elif form.radio.data == 'session':
            data = get_session_logs(shown_data)
    return render_template("logs.html", display_page=display_page, form=form, data=data)
