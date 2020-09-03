# The 'Console dev (legacy)' webpage. A page to show statements thanks to command lines.
# Unfortunately this webpage has been abandonned
from flask import (
    Blueprint, render_template, session, send_file
)
from flaskr.forms import DevForm
import sys
import matplotlib.pyplot as plt
from . import getter, diagrams

class Token:
    def __init__(self, token_type, token_value):
        self.token_type = token_type
        self.token_value = token_value
    
    def __repr__(self):
        return "token_type : " +  self.token_type + ", token_value: " + str(self.token_value)


bp = Blueprint('dev', __name__, url_prefix='')

def create_command_list(lines):
    command_list = []
    for l in lines:
        if l == '' or l.isspace():
            continue
        next_types = ['command']
        current_command = []
        tokens = l.split()
        for t in tokens:
            try:
                expected_type = next_types.pop(0)
            except IndexError:
                raise IndexError("Error in line '" + l + "', didn't expect token " + t)
            if expected_type == 'command':
                if t == 'not':
                    current_command.append(Token('not-command','not'))
                    next_types.append('command')
                elif t == 'has':
                    current_command.append(Token('filter-command','has'))
                    next_types.append('field')
                elif t == 'is':
                    current_command.append(Token('filter-command','is'))
                    next_types.append('field')
                    next_types.append('value')
                elif t == 'show-logs':
                    current_command.append(Token('show-command','logs'))
                elif t == 'make-piechart':
                    current_command.append(Token('show-command','piechart'))
                    next_types.append('field')
                else:
                    raise ValueError("Error in line '" + l + "', expected a command for token " + t)
            elif expected_type == 'field':
                subfields = t.split('\\')
                for i in range(len(subfields)):
                    s = subfields[i]
                    if s.startswith('uri('):
                        id_value = s.split('(')[1][:-1]
                        subfields[i] = getter.get_id_URI(id_value)
                current_command.append(Token('field',subfields))
            elif expected_type == 'value':
                if t.startswith('uri('):
                    id_value = t.split('(')[1][:-1]
                    id_value = getter.get_id_URI(id_value)
                    current_command.append(Token('value', id_value))
                else:
                    current_command.append(Token('value',t))
        if next_types:
            raise ValueError("Error in line '" + l + "' : Missing tokens " + str(next_types))
        command_list.append(current_command)

    return command_list

def filter_statements(filter_command, statements, token_list, not_command):
    print(token_list, file=sys.stdout)
    filtered_statements = []
    if filter_command == 'has':
        field = token_list[0].token_value
        for i in range(len(statements)):
            try:
                field_value = statements[i]
                for key in field:
                    field_value = field_value[key]
                if not not_command:
                    filtered_statements.append(statements[i])
            except KeyError:
                if not_command:
                    filtered_statements.append(statements[i])
    elif filter_command == 'is':
        field = token_list[0].token_value
        value = token_list[1].token_value
        for i in range(len(statements)):
            try:
                field_value = statements[i]
                for key in field:
                    field_value = field_value[key]
                if not not_command and field_value == value:
                    filtered_statements.append(statements[i])
                elif not_command and field_value != value:
                    filtered_statements.append(statements[i])
            except KeyError:
                if not_command:
                    filtered_statements.append(statements[i])
        pass
    return filtered_statements

def show_statements(show_command, statements, next_tokens):
    response_type = 'HTML_data'
    data = []
    if show_command == 'logs':
        data.append('<table>')
        data.append('<th scope="col">Name</th>\n<th scope="col">Verb</th>\n'\
        '<th scope="col">Activity</th>\n<th scope="col">Timestamp</th>')
        for i in range(len(statements), 0, -1):
            s = statements[i-1]
            data.append(getter.statement_HTML_table_row(s))
        data.append('</table>')
    elif show_command == 'piechart':
        piechart_data = {}
        field = next_tokens[0].token_value
        for i in range(len(statements)):
            try:
                field_value = statements[i]
                for key in field:
                    field_value = field_value[key]
                if field_value not in piechart_data.keys():
                    piechart_data[field_value] = 1
                else:
                    piechart_data[field_value] += 1
            except KeyError:
                pass
        response_type = 'HTML_img'
        #TODO: Modifier 
        data = diagrams.piechart_diagram(piechart_data)
    return (response_type, data)


def process_text(dev_text):
    # Process the commands typed by the user
    lines = dev_text.split('\r\n') # Get all commands
    command_list = create_command_list(lines)
    statements = session['statements']
    for c in command_list:
        not_command = False
        for i in range(len(c)):
            token = c[i]
            if token.token_type == 'not-command': # Check which command is called by the user
                not_command = not not_command
            elif token.token_type == 'filter-command':
                statements = filter_statements(token.token_value, statements, c[i+1:], not_command)
                print(len(statements), file=sys.stdout)
                break
            elif token.token_type == 'show-command':
                return show_statements(token.token_value, statements, c[i+1:])
            else:
                raise ValueError('This should be a command ' + str(token))
    return ('HTML_data', [])

@bp.route('/dev', methods=('GET', 'POST'))
def register_dev():
    #Show the 'Console dev(legacy)' webpage
    form = DevForm()
    data = []
    display_page = True
    if form.dev_text.data:
        response = process_text(form.dev_text.data)
        if response[0] == 'HTML_data':
            data = response[1]
        elif response[0] == 'HTML_img':
            return response[1]
        #print(form.dev_text.data.split('\r\n'), file=sys.stdout)
    return render_template("dev.html", display_page=display_page, form=form, data=data)

@bp.route('/id_list', methods=('GET', 'POST'))
def register_id_list():
    id_verbs = getter.id_verbs
    id_activities = getter.id_activities
    id_activity_extensions = getter.id_activity_extensions
    id_context_extensions = getter.id_context_extensions

    return render_template("id_list.html", id_verbs=id_verbs, id_activities=id_activities, id_activity_extensions=id_activity_extensions, \
        id_context_extensions=id_context_extensions)

@bp.route('/exemples', methods=('GET', 'POST'))
def register_examples():
    examples = []
    examples.append(("Afficher les statements ayant pour verbe 'started'",\
        "is statement\\verb\\id uri(started)\n"\
        "show-logs"))
    examples.append(("Afficher les statements de saisie du mot-clé 'def'",\
        "is statement\\object\\definition\\extensions\\uri(keyword-extension) def\n"\
        "show-logs"))
    examples.append(("Enlever les statements de saisie du mot-clé 'def' <br> Afficher tous les autres les statements",\
        "not is statement\\object\\definition\\extensions\\uri(keyword-extension) def\n"\
        "show-logs"))
    examples.append(("Enlever les statements de saisie du mot-clé 'def' <br> Afficher un diagramme sur les mots-clés saisis",\
        "not is statement\\object\\definition\\extensions\\uri(keyword-extension) def\n"\
        "make-piechart statement\\object\\definition\\extensions\\uri(keyword-extension)"))
    return render_template("exemples.html", examples=examples)