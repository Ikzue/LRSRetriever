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

def execution_histogram(sessions, max_scale):
        nb_sessions = len(sessions)
        cols = 3
        rows = nb_sessions // cols
        print(max_scale)

        fig = subplots.make_subplots(rows = 1, cols = 3, shared_xaxes='all', shared_yaxes='all')
        fig.layout.update(title = "Nombre d'executions et de modif d'instructions pour chaque session", barmode="stack")
        for i in range(0, nb_sessions):
                s = sessions[i]
                row = 1 + (i // 3)
                col = 1 + (i % 3)
                session_id = s[0]
                exec_times = s[1]['exec_times']
                instruc_times = s[1]['instruc_times']

                trace_exec =  go.Histogram(x=exec_times,xbins = dict(end = max_scale,size = 300), name="Nb. Exec", legendgroup="Exec")
                trace_instruc =  go.Histogram(x=instruc_times,xbins = dict(end = max_scale, size = 300), name="Instruc")
                fig.append_trace(trace_exec, row, col)
                fig.append_trace(trace_instruc, row, col)
                if i == 2:
                        break
        fig.show()
                