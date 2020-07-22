from flask import session
from . import getter, diagrams
from datetime import datetime, timedelta

class Visu():
    def __init__(self, name, return_type, function):
        self.name = name
        self.return_type = return_type # HTML_data, piechart
        self.function = function

    def __repr__(self):
        return "Visu name: " +  self.name + ", return_type: " + self.return_type + "self.function " + str(self.function)


visu_list = []

### Template : Create your own visualisation

# Define your own function and then append it to visu_list. 
# Your visualisation will then be shown on the '/visu' page of the website as an option.

# Step 1: Define your function
def my_visualisation_function(statements, filters):
    statements = getter.get_filtered_statements(statements, filters)

    # Do whatever you want to do here
    # ...

    return result


# Step 2 : Create a Visu object and Append your function to visu_list
# visu_list.append(Visu('Name_on_website', 'Result_type', my_visualisation_function))

# Now, you should be able to select your visualisation on the website. Below are all the results type available for your function:
'''
string_list : a list of strings displayed as an HTML list
HTML_data: a string containing HTML data
piechart: a python dict of string keys and int labels. The website will make a piechart from this data using plotly.
barchart : a python dict of string keys and int labels. The website will make a barchart from this data.
Image : an image filepath on the server or an image buffer (io.BytesIO())
'''




### 1 : HTML_data: a string of HTML code
def get_stats_visu(statements, filters):
    statements = getter.get_filtered_statements(statements, filters)
    data = []
    session_ids = set()
    num_passed_exec = 0
    num_failed_exec = 0
    for s in statements:
        current_id = getter.get_session_id(s)
        verb = getter.get_verb(s)
        activity = getter.get_activity(s)
        session_ids.add(current_id)
        if activity == 'a programming execution':
            if verb == 'passed':
                num_passed_exec += 1
            if verb == 'failed':
                num_failed_exec += 1
    data.append('Number of current filtered statements : ' + str(len(statements)))
    data.append('Number of sessions : ' + str(len(session_ids)))
    data.append('Number of passed executions:' + str(num_passed_exec))
    data.append('Number of failed executions: ' + str(num_failed_exec))
    return data

visu_list.append(Visu('Statistiques', 'string_list', get_stats_visu))

### 2.1 : piechart : Return a dict of labels and values (eg:{'a': 2, 'b': 5, 'c';9}). The website will make a piechart from this data.

def get_keywords_visu(statements, filters):
    statements = getter.get_filtered_statements(statements, filters)
    keywords = {}
    for s in statements:
        if getter.is_keyword_statement(s):
            kw = getter.get_keyword(s)
            if kw not in keywords.keys():
                keywords[kw] = 1
            else:
                keywords[kw] += 1
    return keywords

visu_list.append(Visu('Mots-clés', 'piechart', get_keywords_visu))

'''
### 2.2 : HTML_data :  The same thing but with HTML_data. 
# With plotly, you can directly send HTML_data from your plot (check diagrams.piechart_diagram)

def get_keywords_visu(statements, filters):
    statements = getter.get_filtered_statements(statements, filters)
    keywords = {}
    for s in statements:
        if getter.is_keyword_statement(s):
            kw = getter.get_keyword(s)
            if kw not in keywords.keys():
                keywords[kw] = 1
            else:
                keywords[kw] += 1
    return diagrams.piechart_diagram(keywords)

visu_list.append(Visu('Mots-clés', 'HTML_data', get_keywords_visu))
'''
'''
### 2.3 : Image : The same thing but with an image made with matplotlib.
def get_keywords_visu(statements, filters):
    statements = getter.get_filtered_statements(statements, filters)
    import matplotlib.pyplot as plt
    import io
    keywords = {}
    for s in statements:
        if getter.is_keyword_statement(s):
            kw = getter.get_keyword(s)
            if kw not in keywords.keys():
                keywords[kw] = 1
            else:
                keywords[kw] += 1
    labels = []
    sizes = []
    for k, v in keywords.items():
        labels.append(k)
        sizes.append(v)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    #plt.savefig(os.path.join('flaskr', 'img', 'line_plot.png'))
    #return os.path.join('img','line_plot.png')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

visu_list.append(Visu('Mots-clés', 'image', get_keywords_visu))
'''


### 3 : HTML_Data: Number of executions
def get_execution_visu(statements, filters):
    statements = getter.get_filtered_statements(statements, filters)
    data = ''
    ord_statements = {}
    filter_interactions = {('opened', 'application'), ('closed', 'application'), ('updated', 'student-number'), ('updated', 'partner-number'),
    ('switched', 'mode'), ('created', 'file'), ('opened', 'file'), ('saved-as', 'file'), ('saved', 'file'), ('copied', 'output-console')}
    max_scale = 0
    
    for s in statements:
        verb, id = getter.get_verb(s), getter.get_activity_parsed_id(s)
        session_id = getter.get_session_id(s)
        timestamp = datetime.strptime(getter.get_timestamp(s), '%Y-%m-%dT%H:%M:%S.%fZ')
        if session_id not in ord_statements.keys():
            ord_statements[session_id] = {'timestamp': timestamp, 'exec_times': [], 'instruc_times' : []}

        delta = timestamp - ord_statements[session_id]['timestamp']
        delta = delta.total_seconds()
        if verb == "started" and id == "execution":
            ord_statements[session_id]['exec_times'].append(delta)
            if delta > max_scale:
                max_scale = delta
        elif verb == "modified" and id == "instruction":
            ord_statements[session_id]['instruc_times'].append(delta)
            if delta > max_scale:
                max_scale = delta
    
    ord_sessions = sorted(ord_statements.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    sorted_sessions = []
    for s in ord_sessions:
        if s[1]['exec_times'] or s[1]['instruc_times']:
            sorted_sessions.append(s)
            print("OK")
        else:
            print("KO")
    #print(sorted_sessions[0])
    diagrams.execution_histogram(sorted_sessions, max_scale)
    return "Mic_ OK"
    '''
    for s in sorted_sessions:
        nb_exec = str(len(s[1]['exec_times']))
        nb_inst = str(len(s[1]['instruc_times']))
        if nb_exec == '0':
            html_row = '<p style="color: red">'
        else:
            html_row = '<p>'
        html_row += '<b> Session timestamp :' + datetime.strftime(s[1]['timestamp'], '%Y-%m-%dT%H:%M:%S')  + ' | Nombre d\'execution  : ' + \
            nb_exec +  ' | Nombre modif. instructions  : ' + nb_inst  + ' | Session ID : ' + s[0] + '</b> </p>\n' 
        data += html_row
    

    return data
    '''

visu_list.append(Visu('Exécutions', 'HTML_data', get_execution_visu))

### 4 : barchart : Return a dict of labels and values (eg:{'a': 2, 'b': 5, 'c';9}). The website will make a barchart from this data.
def get_errors_visu(statements, filters):
    statements = getter.get_filtered_statements(statements, filters)
    errors= {}
    errors_verb_id = { ('received', 'execution-error'), ('received', 'execution-warning'), \
        ('received', 'evaluation-error'), ('received', 'evaluation-warning')}
    
    for s in statements:
        verb, id = getter.get_verb(s), getter.get_activity_parsed_id(s)
        if (verb, id) in errors_verb_id:
            error = getter.get_error_first_group(s)
            if error not in errors.keys():
                errors[error] = 1
            else:
                errors[error] += 1
    return errors

visu_list.append(Visu('Erreurs', 'barchart', get_errors_visu))

### 5 : piechart : Instruction types
def get_instructions_visu(statements, filters):
    statements = getter.get_filtered_statements(statements, filters)
    instructions_type = {}
    
    for s in statements:
        verb, id = getter.get_verb(s), getter.get_activity_parsed_id(s)
        if (verb, id)  == ('modified', 'instruction'):
            s_type = getter.get_instruction_type(s)
            if s_type not in instructions_type.keys():
                instructions_type[s_type] = 1
            else:
                instructions_type[s_type] += 1
    return instructions_type

visu_list.append(Visu('Instructions', 'piechart', get_instructions_visu))
