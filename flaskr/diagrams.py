from flask import send_file
import io, os
from PIL import Image

from plotly.offline import plot
from plotly import subplots
import plotly.graph_objs as go


def piechart_diagram(data):
    labels = []
    values = []
    for k, v in data.items():
            labels.append(k)
            values.append(v)

    trace = go.Pie(labels = labels,
            values = values)
    data = [trace]
    div = plot({'data': data}, output_type="div")
    return div

def barchart_diagram(data):
    x = []
    y = []
    for k, v in data.items():
            x.append(k)
            y.append(v)

    trace = go.Bar(x = x,
            y = y)
    data = [trace]
    div = plot({'data': data}, output_type="div")
    return div

def execution_histogram(sessions, max_scale, page_number):
        page_length = 6
        begin = page_number * page_length
        end = begin + page_length
        previous_page = page_number - 1
        next_page = page_number + 1
        if previous_page < 0:
                previous_page = 'None'
        if end > len(sessions):
                next_page = 'None'
        HTML_text = "<h3>Nombre d'executions (bleu) et de modification d'instructions (rouge) par session </h3>"
        for s in sessions[begin:end]:
                session_id = s[0]
                exec_times = s[1]['exec_times']
                instruc_times = s[1]['instruc_times']
                title = s[1]['timestamp'].strftime('%Y-%m-%d %H:%M:%S') + ' Session:' + s[0]
                trace_exec =  go.Histogram(x=exec_times,xbins = dict(start = 0, end = max_scale,size = 300), autobinx=False, 
                name="Nombre d'exécutions")
                trace_instruc =  go.Histogram(x=instruc_times,xbins = dict(start = 0,end = max_scale, size = 300), autobinx=False, 
                name="Nombre d'instructions saisies")
                data = [trace_exec, trace_instruc]
                layout = {'title': title, 'barmode': 'stack', 'xaxis':{'range':[0,max_scale], 'title': 'Temps(en secondes)'}}
                fig = go.Figure(data=data, layout=layout)
                HTML_text += plot(fig, output_type="div")
        return previous_page, next_page, HTML_text