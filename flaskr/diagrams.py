# Show graphical representations from data structures with the plotly library
from flask import send_file
import io, os
from PIL import Image

from plotly.offline import plot
from plotly import subplots
import plotly.graph_objs as go


def piechart_diagram(data):
    #Show a piechart from a dict {(str:int)*}
    labels = []
    values = []
    print(data)
    for k, v in data.items():
            labels.append(k)
            values.append(v)

    trace = go.Pie(labels = labels,
            values = values)
    data = [trace]
    div = plot({'data': data}, output_type="div", include_plotlyjs=False)
    return div

def barchart_diagram(data):
    #Show a piechart from a dict {(str:int)*}
    x = []
    y = []
    for k, v in data.items():
            x.append(k)
            y.append(v)

    trace = go.Bar(x = x,
            y = y)
    data = [trace]
    div = plot({'data': data}, output_type="div", include_plotlyjs=False)
    return div

def timeline_diagram(size, data):
    #Print a timeline. size: the timeline's interval. data: the timeline data as a list of tuples [(str, int)*].
    figure_values = {elem[0]:[] for elem in data}
    i = 0
    for elem in data:
        category = elem[0]
        y_value = elem[1]
        for key, y_values in figure_values.items():
            if key == category:
                for j in range(y_value):
                        y_values.append(i)
        i += size
    fig = go.Figure()
    x = [size*i for i in range(len(data))]
    for key in figure_values:
        #fig.add_trace(go.Bar(x=x,y=figure_values[key], ))
        fig.add_trace(go.Histogram(x=figure_values[key] ,xbins = dict(start = -0.001,size = size), autobinx=False, 
        name=key))
    fig.update_layout(title='Timeline', barmode='stack',  xaxis={'range':[0,size*len(data)]})
    return plot(fig, output_type="div", include_plotlyjs=False)

def histogram_diagram(data, title, interval_size, x_label, x_size):
    # data : list of histogram values. 
    histo =  go.Histogram(x=data,xbins = dict(start = 0, size = interval_size))
    data = [histo]
    layout = {'title': title, 'barmode': 'stack', 'xaxis':{'range':[0, x_size], 'title': x_label}}
    fig = go.Figure(data=data, layout=layout)
    return plot(fig, output_type="div", include_plotlyjs=False)


def state_barchart(s):
    # A barchart made to specifically work with the 'Etat(Sessions)' visualisation.
    title = s[1]['timestamp'].strftime('%Y-%m-%d %H:%M:%S') + ' Session:' + s[0]
    state_times = s[1]['state_times']
    previous_state, previous_timestamp = state_times[0]
    data = []
    layout = {'title': title, 'barmode': 'stack'}
    legend_color = {'interacting-state' : {'color':'rgb(255, 0, 0)', 'show_legend':True},
        'idle-state': {'color': 'rgb(0, 255, 0)','show_legend': True}, 
        'typing-state' : {'color': 'rgb(0, 0, 255)', 'show_legend':True}}

    for state, timestamp in state_times[1:]:
        delta = (timestamp - previous_timestamp).total_seconds()
        color = legend_color[previous_state]['color']
        show_legend = legend_color[previous_state]['show_legend']
        data.append(go.Bar(name=previous_state, x=[delta], y=['Evolution de l\'etat (secondes)'], 
        legendgroup=previous_state, orientation='h', marker_color=color, showlegend=show_legend))
        legend_color[previous_state]['show_legend'] = False     
        previous_state, previous_timestamp = state, timestamp

    last_delta = s[1]['last_state_delta']
    color = legend_color[previous_state]['color']
    show_legend = legend_color[previous_state]['show_legend']
    data.append(go.Bar(name=previous_state, x=[last_delta], y=['Evolution de l\'etat (secondes)'], legendgroup=previous_state, 
    orientation='h', marker_color=color, showlegend=show_legend))
    fig = go.Figure(data=data, layout=layout)

    return plot(fig, output_type="div", include_plotlyjs=False)