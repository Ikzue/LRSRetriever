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

def timeline_diagram(size, data):
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
        return plot(fig, output_type="div")
        '''
        years = [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
                2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=years,
                        y=[0, 146, 112, 127, 124, 180, 236, 207, 236, 263,
                        350, 430, 474, 526, 488, 537, 500, 439],
                        name='Rest of world',
                        marker_color='rgb(55, 83, 109)'
                        ))
        fig.add_trace(go.Bar(x=years,
                        y=[4, 13, 10, 11, 28, 37, 43, 55, 56, 88, 105, 156, 270,
                        299, 340, 403, 549, 499],
                        marker_color='rgb(26, 118, 255)'
                        ))

        fig.update_layout(
        title='US Export of Plastic Scrap',
        xaxis_tickfont_size=14,
        yaxis=dict(
                title='USD (millions)',
                titlefont_size=16,
                tickfont_size=14,
        ),
        legend=dict(
                x=0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1 # gap between bars of the same location coordinate.
        )
        fig.show()
        '''

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
        HTML_text = "<h3>Evolution du nombre d'executions par session </h3>"
        for s in sessions[begin:end]:
                session_id = s[0]
                exec_times = s[1]['exec_times']
                instruc_times = s[1]['instruc_times']
                title = s[1]['timestamp'].strftime('%Y-%m-%d %H:%M:%S') + ' Session:' + s[0]

                trace_exec =  go.Histogram(x=exec_times,xbins = dict(start = 0, end = max_scale,size = 300), autobinx=False, 
                name="Nombre d'exécutions")
                trace_instruc =  go.Histogram(x=instruc_times,xbins = dict(start = 0,end = max_scale, size = 1), autobinx=False, 
                name="Nombre d'instructions saisies")
                data = [trace_exec, trace_instruc]
                #layout = {'title': title, 'barmode': 'stack', 'xaxis':{'range':[0,max_scale], 'title': 'Temps(en secondes)'}}
                layout = {'title': title, 'barmode': 'stack', 'xaxis':{'rangemode':'tozero', 'title': 'Temps(en secondes)'}}
                fig = go.Figure(data=data, layout=layout)
                HTML_text += plot(fig, output_type="div")
        return previous_page, next_page, HTML_text


def state_barchart(sessions, page_number):
        page_length = 6
        begin = page_number * page_length
        end = begin + page_length
        previous_page = page_number - 1
        next_page = page_number + 1
        print(len(sessions))
        HTML_text = "<h3>Etat de l'utilisateur en fonction du temps</h3>"
        if previous_page < 0:
                previous_page = 'None'
        if end > len(sessions):
                next_page = 'None'
        for s in sessions[begin:end]:
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
                HTML_text += plot(fig, output_type="div")
        return previous_page, next_page, HTML_text
        '''
        fig = go.Figure(data=[
        go.Bar(name='SF Zoo', y=animals, x=[20], marker_color='rgb(55, 83, 109)', legendgroup="group",orientation='h'),
        go.Bar(name='LA Zoo', y=animals, x=[12],orientation='h'),
        go.Bar(name='SF Zoo', y=animals, x=[18], marker_color='rgb(55, 83, 109)', legendgroup="group", showlegend=False,orientation='h'),
        ])
        # Change the bar mode
        fig.update_layout(barmode='stack')
        #fig.show()
        '''