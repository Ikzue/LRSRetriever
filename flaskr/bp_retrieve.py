# The "Retrieve statements" webpage used to get the statements from the LRS.

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, session
)
from flaskr.forms import RetrieveForm
import requests, json, sys, datetime
import hashlib

bp = Blueprint('retrieve', __name__, url_prefix='')

def get_date(form_date):
    # Get the minimum date of the retrieved statements
    if form_date == 'today':
        date = datetime.datetime.today().utcnow()
    elif form_date == 'week':
        date = datetime.datetime.today().utcnow() - datetime.timedelta(days=7)
    elif form_date == 'month':
        date = datetime.datetime.today().utcnow() - datetime.timedelta(days=30)
    else:
        return ''
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    return date.isoformat() + 'Z'

    
def get_statements(form_number_list, form_hash_list, selected_date):
    # Get the statements from the LRS with the form info
    url = 'https://lrsmocah.lip6.fr/api/statements/aggregate'
    auth = 'Basic Yzc1NjdmNTZhNGRjOTk2MWU5OTY2NzE5ZDZmZDQ4YzhjZDc4MGY0MzpjYTY4MDQ5ODhmZGU0N2QyZThjYzQyMmUxNzQ3ZmJkMjg0NGEwNjY0'
    headers = {'Authorization': auth}
    date = get_date(selected_date)
    all_hashes = ''

    # Convert and get all student numbers
    number_list = form_number_list.split(';')
    for number in number_list:
        if number != '':
            my_hash = hashlib.sha1(str.encode(number))
            my_hash = my_hash.hexdigest()[:10]
            all_hashes += my_hash + '|'

    # Get all hashes
    form_hash_list = form_hash_list.replace('|', '\|')
    hash_list = form_hash_list.split(';')
    for my_hash in hash_list:
        if my_hash != '':
            all_hashes += my_hash + '|'

    if all_hashes.endswith('|'):
        all_hashes = all_hashes[:-1]

    #Get statements from hash numbers
    pipeline_params = [{'$project': { 'statement': 1, '_id': 0 , 'timestamp': 1}}]


    match = {'$match': {
        'statement.actor.name': {'$regex':all_hashes},
    }}
    
    # A first request to get all session IDs
    if date:
        match['$match']['statement.timestamp'] = {'$gte':{'$dte':date}}
    pipeline_params.append(match)
    params = {'pipeline': json.dumps(pipeline_params)}
    r = requests.get(url, params=params,headers=headers, verify=False)
    statements = json.loads(r.text)

    # A second request to get all the statements with the session IDs. Used in case a student identifies themselves late.
    sessions = set()
    for s in statements:
        bugged_statements = ['2020-07-08T09:08:18.077Z', '2020-07-08T09:36:51.475Z'] # Small hack to remove old bugged statement...
        if s['timestamp'] in bugged_statements:
            continue
        sessions.add(s['statement']['context']['extensions']['https://www.lip6.fr/mocah/invalidURI/extensions/session-id'])
    sessions = list(sessions)
    
    pipeline_params = [{'$project': { 'statement': 1, '_id': 0 ,'timestamp':1}}]
    match = {'$match': {
        'statement.context.extensions.https://www&46;lip6&46;fr/mocah/invalidURI/extensions/session-id': {'$in': sessions},
    }}
    if date:
        match['$match']['statement.timestamp'] = {'$gte':{'$dte':date}}
    pipeline_params.append(match)
    pipeline_params.append({'$sort':{
          'statement.timestamp': -1,
          '_id': 1
    }})
    params = {'pipeline': json.dumps(pipeline_params)}
    r = requests.get(url, params=params,headers=headers, verify=False)
    statements = json.loads(r.text)
    return statements

@bp.route('/', methods=('GET', 'POST'))
@bp.route('/index', methods=('GET', 'POST'))
def register():
    # Show the page with the form
    form=RetrieveForm()
    statements = {}
    nb_statements = None
    if form.validate_on_submit():
        statements = get_statements(form.number_list.data, form.hash_list.data, form.date.data)
        statements.reverse()
        session['statements'] = statements
        #print(len(session['statements']), file=sys.stdout)
        nb_statements = len(statements)
        
    return render_template('index.html', statements=statements, nb_statements=nb_statements,form=form)

