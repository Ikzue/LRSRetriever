import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

import requests, json, sys, datetime

bp = Blueprint('retrieve', __name__, url_prefix='')

def get_date(form_date):
    if form_date == "today":
        date = datetime.datetime.today().utcnow()
    elif form_date == "week":
        date = datetime.datetime.today().utcnow() - datetime.timedelta(days=7)
    elif form_date == "month":
        date = datetime.datetime.today().utcnow() - datetime.timedelta(days=30)
    else:
        return ""
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    return date.isoformat() + "Z"
    pass
    
def get_statements(form):
    url = "https://lrsmocah.lip6.fr/api/statements/aggregate"
    auth = "Basic Yzc1NjdmNTZhNGRjOTk2MWU5OTY2NzE5ZDZmZDQ4YzhjZDc4MGY0MzpjYTY4MDQ5ODhmZGU0N2QyZThjYzQyMmUxNzQ3ZmJkMjg0NGEwNjY0"
    headers = {"Authorization": auth}
    #pipeline_params = [{"$limit": 1}, {"$project": { "statement": 1, "_id": 0 }}]
    pipeline_params = [{"$project": { "statement": 1, "_id": 0 ,"timestamp":1}}]
    date = get_date(form["date"])
    match = {"$match": {
        "statement.actor.name": {"$regex":"{}".format(form['student-hash'])},
        "statement.verb.id": {"$regex":"{}".format(form['verb-name'])},
        "statement.object.id": {"$regex":"{}".format(form['activity-name'])},
    }}
    if date:
        match["$match"]["timestamp"] = {"$gte":{"$dte":date}}
    
        
    #match["$match"]
    print(match, file=sys.stdout)
    pipeline_params.append(match)
    #{ "$dateToString": {"date": "2020-06-15T09:57:47.967Z"} }
    params = {"pipeline": json.dumps(pipeline_params)}
    #params = {"$limit": 1, "$project": {"statement": 1, "_id": 0, "timestamp":1}}
    r = requests.get(url, params=params,headers=headers, verify=False)
    statements = json.loads(r.text)
    return statements

@bp.route('/index', methods=('GET', 'POST'))
def register():
    statements = {}
    nb_statements = None
    if request.method == 'POST':
        student_hash = request.form['student-hash']
        verb_name = request.form['verb-name']
        activity_name = request.form['activity-name']
        statements = get_statements(request.form)
        nb_statements = len(statements)
    return render_template("index.html", statements=statements, nb_statements=nb_statements)

"""
        print(request.form, file=sys.stdout)
        student_hash = request.form['student-hash']
        verb_name = request.form['verb-name']
        activity_name = request.form['activity-name']
"""