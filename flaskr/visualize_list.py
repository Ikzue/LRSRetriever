# A module to add your own analysis/visualisations thanks to a template. 
# Define your analysis/visualisation function and add it to visu_list with the type of the returned value of your function.
# Simple return types : HTML_data, piechart, string_list, barchart, Image
# Complex return types : multiple_page_HTML, multiple_histogram
from flask import session
from . import getter, diagrams
from datetime import datetime, timedelta

class Visu():
    def __init__(self, name, return_type, function):
        self.name = name
        self.return_type = return_type # HTML_data, piechart, string_list, barchart, Image
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


# After that, you should be able to select your visualisation on the website. Below are all the results type available for your function:
'''
string_list : a list of strings displayed as an HTML list
HTML_data: a string containing HTML data
piechart: a python dict of string keys and int labels. The website will make a piechart from this data using plotly.
barchart : a python dict of string keys and int labels. The website will make a barchart from this data.
Image : an image filepath on the server or an image buffer (io.BytesIO())
'''




### Example 1 : HTML_data: a string of HTML code
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



### 3: barchart : Return a dict of labels and values (eg:{'a': 2, 'b': 5, 'c';9}). The website will make a barchart from this data.
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



### Multiple HTML

### 4: : multiple_histogram: Number of executions
def get_execution_visu(statements, filters):
    statements = getter.get_filtered_statements(statements, filters)
    data = ''
    ord_statements = {}    
    
    for s in statements:
        verb, id = getter.get_verb(s), getter.get_activity_parsed_id(s)
        session_id = getter.get_session_id(s)
        timestamp = datetime.strptime(getter.get_timestamp(s), '%Y-%m-%dT%H:%M:%S.%fZ')
        if session_id not in ord_statements.keys():
            ord_statements[session_id] = {'timestamp': timestamp, 'exec_times': [], 'session_length' : 0}
        current_session = ord_statements[session_id]

        delta = timestamp - current_session['timestamp']
        delta = delta.total_seconds()
        if verb == "started" and id == "execution":
            current_session['exec_times'].append(delta)
        if delta > ord_statements[session_id]['session_length']:
            current_session['session_length'] = delta
    
    ord_sessions = sorted(ord_statements.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    sorted_sessions = []
    for s in ord_sessions:
        if s[1]['exec_times']:
            title = s[1]['timestamp'].strftime('%Y-%m-%d %H:%M:%S') + ' Session : ' + s[0] + ' Length : ' + str(s[1]['session_length']) + 's'
            values = s[1]['exec_times']
            x_axis_size = s[1]['session_length']
            sorted_sessions.append((title, values, x_axis_size))
    
    values = {'x_axis' : 'Temps en secondes', 'values' : sorted_sessions}
    return values

visu_list.append(Visu('Exécutions(Sessions)', 'multiple_histogram', get_execution_visu))

# 5 : multiple_page_HTML: State of the student
def get_state_visu(statements, filters):
    statements = getter.get_filtered_statements(statements, filters)
    data = ''
    ord_statements = {}    
    
    for s in statements:
        verb, id = getter.get_verb(s), getter.get_activity_parsed_id(s)
        session_id = getter.get_session_id(s)
        timestamp = datetime.strptime(getter.get_timestamp(s), '%Y-%m-%dT%H:%M:%S.%fZ')
        if session_id not in ord_statements.keys():
            ord_statements[session_id] = {'timestamp': timestamp, 'last_state_delta': 0, 'state_times': [('idle-state', timestamp)]}
        current_session = ord_statements[session_id]

        if verb == 'entered' and 'state' in id:
            current_session['last_state_delta'] = 0
            current_session['state_times'].append((id,timestamp))
        else:
            last_timestamp = ord_statements[session_id]['state_times'][-1][1]
            delta_time = (timestamp - last_timestamp).total_seconds()
            current_session['last_state_delta'] = delta_time
    
    ord_sessions = sorted(ord_statements.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    HTML_divs = []
    for s in ord_sessions:
        HTML_divs.append(diagrams.state_barchart(s))
    return HTML_divs

visu_list.append(Visu('Etat(Sessions)', 'multiple_page_HTML', get_state_visu))


## 6 : Dummy Timeline: Takes a tuple (int, [(string, int)*]) -- (timeline_interval, [(category_name, y_value)]) and creates a timeline
## Timeline template
def timeline_function(statements, filters):
    statements = getter.get_filtered_statements(statements, filters)

    timeline_interval = 1
    timeline_data = [('Catégorie A', 3), ('Catégorie B', 1), ('Catégorie B', 1), ('void', 0), ('Catégorie C', 4), ('Catégorie C', 2)]

    return timeline_interval, timeline_data

visu_list.append(Visu('Dummy timeline', 'timeline', timeline_function))


''' Template
def my_analysis_function(statements, filters):
    statements = getter.get_filtered_statements(statements, filters) # Get all fetched statements in a list
    
    # Do your analysis here
    # ...

    return result

visu_list.append(Visu('Name_on_website', 'Result_type', my_analysis_function))
'''
