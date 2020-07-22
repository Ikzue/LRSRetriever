from flask import session
import hashlib

def get_actor_name(statement):
    return statement['statement']['actor']['name']

def get_session_id(statement):
    return statement['statement']['context']['extensions']['https://www.lip6.fr/mocah/invalidURI/extensions/session-id']

def get_timestamp(statement):
    return statement['statement']['timestamp']

def get_verb(statement):
    return statement['statement']['verb']['display']['en-US']


def get_activity(statement):
    return statement['statement']['object']['definition']['name']['en-US']

def get_activity_parsed_id(statement):
    return statement['statement']['object']['id'].split('/')[-1]

def get_error_first_group(statement):
    return statement['statement']['object']['definition']['extensions']['https://www.lip6.fr/mocah/invalidURI/extensions/first-group']
    
def get_keyword(statement):
    return statement['statement']['object']['definition']['extensions']['https://www.lip6.fr/mocah/invalidURI/extensions/keyword-typed']

def get_instruction_type(statement):
    return statement['statement']['object']['definition']['extensions']['https://www.lip6.fr/mocah/invalidURI/extensions/new-instruction-type']

def is_keyword_statement(statement):
    return get_verb(statement) == 'typed' and get_activity(statement) == "a keyword"

def statement_HTML_table_row(s, show_extensions=False):
    info = '<tr>'
    info += '<td>' + s['statement']['actor']['name'] + '</td>'
    info += '<td>' + s['statement']['verb']['display']['en-US'] + '</td>'
    info += '<td>' + s['statement']['object']['definition']['name']['en-US'] + '</td>'
    info += '<td>' + s['statement']['timestamp'][:19] + '</td>'
    if show_extensions:
        try:
            extensions_info = '<td>'
            for k,v in s['statement']['object']['definition']['extensions'].items():
                extensions_info += k.split('/')[-1] + ' : ' + str(v) + '<br>'
            extensions_info += '</td>'
            info += extensions_info
        except KeyError:
            info += '<td> No activity extensions</td>'
    info += "</tr>"
    return info

def statement_info(s, show_extensions):
    info = s['statement']['actor']['name']
    info += ' ' + s['statement']['verb']['display']['en-US']
    info += ' ' + s['statement']['object']['definition']['name']['en-US']
    if show_extensions:
        info = '<strong>' + info + '</strong>'
        try:
            extensions_info = ', extensions:'
            for k,v in s['statement']['object']['definition']['extensions'].items():
                extensions_info += ' ' +  k.split('/')[-1] + ' : ' + str(v) + ','
            if extensions_info.endswith(','):
                extensions_info = extensions_info[:-1]
            info += extensions_info
        except KeyError:
            pass
    return info

def filter_statement_hashes_id(statement, list_hashes, list_ids):
    filter_statement = False
    
    if len(list_hashes) > 0:
        filter_statement = True
        actor_name = get_actor_name(statement)
        for student_hash in list_hashes:
            if student_hash in actor_name:
                filter_statement = False
                break
        if filter_statement:
            return True

    if len(list_ids) > 0:
        filter_statement = True
        statement_session_id = get_session_id(statement)
        for session_id in list_ids:
            if session_id in statement_session_id:
                filter_statement = False
                break
        if filter_statement:
            return True
    return filter_statement
    

def get_filtered_statements(statements, filters = None):
    if filters is None or (len(filters['hashes']) == 0 and len(filters['session-ids']) == 0):
        return statements.copy()

    filtered_statements = []
    list_hashes = filters['hashes']
    list_ids = filters['session-ids']
    for statement in session['statements']:
        if not filter_statement_hashes_id(statement, list_hashes, list_ids):
            filtered_statements.append(statement)
    return filtered_statements
        

def statements_in_session():
    if 'statements' not in session.keys() or len(session['statements']) == 0:
        return False
    return True

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
    return hashes

def get_session_ids(session_ids):
    ids = []
    session_ids = session_ids.split(';')
    for s in session_ids:
        if s != '':
            ids.append(s)
    return ids

def get_id_URI(s_id):
    if s_id in id_verbs:
        return id_verbs[s_id]
    elif s_id in id_activities:
        return id_activities[s_id]
    if s_id in id_context_extensions:
        return id_context_extensions[s_id]
    if s_id in id_activity_extensions:
        return id_activity_extensions[s_id]
    raise ValueError('Couldn\'t find this id: ' + s_id)

id_verbs = {"opened": "http://activitystrea.ms/schema/1.0/open",
    "closed": "http://activitystrea.ms/schema/1.0/close",
    "created": "http://activitystrea.ms/schema/1.0/create",
    "saved": "http://activitystrea.ms/schema/1.0/save",
    "saved-as": "https://www.lip6.fr/mocah/invalidURI/verbs/save-as",
    "switched": "https://www.lip6.fr/mocah/invalidURI/verbs/switched",
    "started": "http://activitystrea.ms/schema/1.0/start",
    "passed": "http://adlnet.gov/expapi/verbs/passed",
    "failed": "http://adlnet.gov/expapi/verbs/failed",
    "terminated": "http://activitystrea.ms/schema/1.0/terminate",
    "received": "http://activitystrea.ms/schema/1.0/receive",
    "typed": "https://www.lip6.fr/mocah/invalidURI/verbs/typed",
    "modified": "https://www.lip6.fr/mocah/invalidURI/verbs/modified",
    "deleted": "http://activitystrea.ms/schema/1.0/delete",
    "inserted": "http://activitystrea.ms/schema/1.0/insert",
    "copied": "https://www.lip6.fr/mocah/invalidURI/verbs/copied",
    "undid": "https://www.lip6.fr/mocah/invalidURI/verbs/undid",
    "redid": "https://www.lip6.fr/mocah/invalidURI/verbs/redid",
    "initialized": "http://activitystrea.ms/schema/1.0/initialized",
    "updated": "http://activitystrea.ms/schema/1.0/update",
    "entered": "https://www.lip6.fr/mocah/invalidURI/verbs/entered"}

id_activities = {"application": "http://activitystrea.ms/schema/1.0/application",
    "student-number": "https://www.lip6.fr/mocah/invalidURI/activity-types/student-number",
    "partner-number": "https://www.lip6.fr/mocah/invalidURI/activity-types/partner-number",
    "file": "http://activitystrea.ms/schema/1.0/file",
    "mode-activity": "https://www.lip6.fr/mocah/invalidURI/activity-types/mode",
    "output-console": "https://www.lip6.fr/mocah/invalidURI/activity-types/output-console",
    "execution": "https://www.lip6.fr/mocah/invalidURI/activity-types/execution",
    "evaluation": "https://www.lip6.fr/mocah/invalidURI/activity-types/evaluation",
    "execution-error": "https://www.lip6.fr/mocah/invalidURI/activity-types/execution-error",
    "execution-warning": "https://www.lip6.fr/mocah/invalidURI/activity-types/execution-warning",
    "evaluation-error": "https://www.lip6.fr/mocah/invalidURI/activity-types/evaluation-error",
    "evaluation-warning": "https://www.lip6.fr/mocah/invalidURI/activity-types/evaluation-warning",
    "keyword-activity": "https://www.lip6.fr/mocah/invalidURI/activity-types/keyword",
    "instruction": "https://www.lip6.fr/mocah/invalidURI/activity-types/instruction",
    "sequence": "https://www.lip6.fr/mocah/invalidURI/activity-types/sequence",
    "text": "https://www.lip6.fr/mocah/invalidURI/activity-types/text",
    "typing-state": "https://www.lip6.fr/mocah/invalidURI/activity-types/typing-state",
    "interacting-state": "https://www.lip6.fr/mocah/invalidURI/activity-types/interacting-state",
    "idle-state": "https://www.lip6.fr/mocah/invalidURI/activity-types/idle-state"}

id_context_extensions = {"session-id": "https://www.lip6.fr/mocah/invalidURI/extensions/session-id",
    "machine-id": "https://www.lip6.fr/mocah/invalidURI/extensions/machine-id",
    "input-context": "https://www.lip6.fr/mocah/invalidURI/extensions/input-context"}

id_activity_extensions =  {"mode-extension": "https://www.lip6.fr/mocah/invalidURI/extensions/mode",
    "old-hash": "https://www.lip6.fr/mocah/invalidURI/extensions/old-hash",
    "new-hash": "https://www.lip6.fr/mocah/invalidURI/extensions/new-hash",
    "input-mode": "https://www.lip6.fr/mocah/invalidURI/extensions/input-mode",
    "old-tab": "https://www.lip6.fr/mocah/invalidURI/extensions/old-tab",
    "closed-tab": "https://www.lip6.fr/mocah/invalidURI/extensions/closed-tab",
    "current-tab": "https://www.lip6.fr/mocah/invalidURI/extensions/current-tab",
    "line-number": "https://www.lip6.fr/mocah/invalidURI/extensions/line-number",
    "function-context": "https://www.lip6.fr/mocah/invalidURI/extensions/function-context",
    "filename": "https://www.lip6.fr/mocah/invalidURI/extensions/filename",
    "old-filename": "https://www.lip6.fr/mocah/invalidURI/extensions/old-filename",
    "new-filename": "https://www.lip6.fr/mocah/invalidURI/extensions/new-filename",
    "keyword-extension": "https://www.lip6.fr/mocah/invalidURI/extensions/keyword-typed",
    "copied-text": "https://www.lip6.fr/mocah/invalidURI/extensions/copied-text",
    "sequence-list": "https://www.lip6.fr/mocah/invalidURI/extensions/sequence-list",
    "text": "https://www.lip6.fr/mocah/invalidURI/extensions/text",
    "index": "https://www.lip6.fr/mocah/invalidURI/extensions/index",
    "first-index": "https://www.lip6.fr/mocah/invalidURI/extensions/first-index",
    "last-index": "https://www.lip6.fr/mocah/invalidURI/extensions/last-index",
    "instruction": "https://www.lip6.fr/mocah/invalidURI/extensions/instruction",
    "old-instruction": "https://www.lip6.fr/mocah/invalidURI/extensions/old-instruction",
    "new-instruction": "https://www.lip6.fr/mocah/invalidURI/extensions/new-instruction",
    "nb-errors": "https://www.lip6.fr/mocah/invalidURI/extensions/nb-errors",
    "nb-warnings": "https://www.lip6.fr/mocah/invalidURI/extensions/nb-warnings",
    "number-asserts": "https://www.lip6.fr/mocah/invalidURI/extensions/number-asserts",
    "severity": "https://www.lip6.fr/mocah/invalidURI/extensions/severity",
    "type": "https://www.lip6.fr/mocah/invalidURI/extensions/type",
    "class": "https://www.lip6.fr/mocah/invalidURI/extensions/class",
    "message": "https://www.lip6.fr/mocah/invalidURI/extensions/message"}