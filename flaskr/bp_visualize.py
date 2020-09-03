# The "Visualisations" webpage used to show visualisations from the retrieved statements.
from flask import (
    Blueprint, render_template, session, send_file, request
)
from flaskr.forms import VisuForm, VisuPrevSuivForm
from . import getter, diagrams
import ast

bp = Blueprint('visualise', __name__, url_prefix='')
PAGE_LENGTH = 6
HISTOGRAM_INTERVAL = 1

def check_prev_next_pages(max_pages, current_page):
    # If there are multiple pages of visualisations, return the previous and next page
    previous_page = 'None'
    next_page = 'None'
    if current_page == 1:
        previous_page = 'None'
    else:
        previous_page = current_page - 1 
    if current_page >= max_pages:
        next_page = 'None'
    else:
        next_page = current_page + 1
    return previous_page, current_page, next_page


@bp.route('/visu', methods=('GET', 'POST'))
def register_visu():
    # Primary form, used to select a visualisation
    form = VisuForm()
    # Secondary form, to turn pages whenever there are multiple visualisations. 
    # (Whenever return type of the analysis is 'multiple_page_HTML' or 'multiple_histogram')
    form2 = VisuPrevSuivForm()
    # Used to show what we want. Differs according to the number of pages, the currentpage, and whether the analysis is'multiple_page_HTML' or
    # 'multiple_histogram'. (Histograms enables user to change the histogram's interval value, so 'refresh_page' and 'is_histogram' are true)
    form2_status = {'show' : False, 'prev_page' : False, 'refresh_page' : False, 'next_page' : False, 'info' : '', 'is_histogram' : False}
    data = ''
    display_page = getter.statements_in_session()
    if display_page: # If there are retrieved statements, we show the webpage
        if form.submit.data and form.validate(): # User selected a visualisation
            return_type, function = form.get_visu_fun(form.radio.data)
            hashes = getter.get_hashes(form.number_list.data, form.hash_list.data)
            session_ids = getter.get_session_ids(form.session_id.data)
            filters = {'hashes' : hashes, 'session-ids' : session_ids}
            if return_type == 'string_list':
                string_list = function(session['statements'], filters)
                data += '<ul>'
                for string in string_list:
                    data += '<li>' +  string + '</li>'
                data += '</ul>'
            elif return_type == 'HTML_data':
                data = function(session['statements'], filters)
            elif return_type == 'piechart':
                pie_data = function(session['statements'], filters)
                data = diagrams.piechart_diagram(pie_data)
            elif return_type == 'barchart':
                bar_data = function(session['statements'], filters)
                data = diagrams.barchart_diagram(bar_data)
            elif return_type == 'image':
                img = function(session['statements'], filters)
                return send_file(img, mimetype='image/jpeg', cache_timeout=0)
            elif return_type == 'timeline':
                timeline_interval, timeline_data = function(session['statements'], filters)
                data = diagrams.timeline_diagram(timeline_interval, timeline_data)
            elif return_type == 'multiple_page_HTML' or return_type == 'multiple_histogram':
                current_page = 1
                if return_type == 'multiple_page_HTML':
                    HTML_divs = function(session['statements'], filters)
                    session['data_' + form.radio.data] = HTML_divs
                    max_pages = (len(HTML_divs) + (PAGE_LENGTH - 1))  // PAGE_LENGTH
                    end = current_page * PAGE_LENGTH
                    begin = end - PAGE_LENGTH
                    for div in HTML_divs[begin:end]:
                        data += div
                elif return_type == 'multiple_histogram':
                    form2_status['is_histogram'] = True
                    form2_status['refresh_page'] = True
                    values = function(session['statements'], filters)
                    session['data_' + form.radio.data] = values
                    x_axis_label = values['x_axis']
                    histogram_values = values['values']
                    max_pages = (len(histogram_values) + (PAGE_LENGTH - 1))  // PAGE_LENGTH
                    end = current_page * PAGE_LENGTH
                    begin = end - PAGE_LENGTH
                    for h in histogram_values[begin:end]:
                        title = h[0]
                        values = h[1]
                        x_axis_size = h[2]
                        data += diagrams.histogram_diagram(values, title, HISTOGRAM_INTERVAL, x_axis_label, x_axis_size)
                
                previous_page, current_page, next_page = check_prev_next_pages(max_pages, current_page)
                function_name = form.radio.data
                form2 = VisuPrevSuivForm(function_name=function_name, prev_number=previous_page, current_number=current_page,
                 next_number=next_page, return_type=return_type, histogram_interval=HISTOGRAM_INTERVAL)
                form2_status['show'] = True
                form2_status['prev_page'] = (previous_page != 'None')
                form2_status['next_page'] = (next_page != 'None')
                form2_status['info'] = 'Page : ' + str(current_page) + '/' + str(max_pages)
            else:
                raise ValueError("Ce type de retour n'est pas défini: " + return_type)
        elif (form2.prev_page.data or form2.refresh_page.data or form2.next_page.data) and form2.validate(): # User turned pages
            if form2.prev_page.data:
                current_page = int(form2.prev_number.data)
            elif form2.next_page.data:
                current_page = int(form2.next_number.data)
            elif form2.refresh_page.data:
                current_page = int(form2.current_number.data)
            return_type = form2.return_type.data
            if return_type == 'multiple_page_HTML':
                HTML_divs = session['data_' + form2.function_name.data]
                max_pages = (len(HTML_divs) + (PAGE_LENGTH - 1))  // PAGE_LENGTH
                end = current_page * PAGE_LENGTH
                begin = end - PAGE_LENGTH
                for div in HTML_divs[begin:end]:
                    data += div
            elif return_type == 'multiple_histogram':
                if form2.histogram_interval.data:
                    histogram_size = float(form2.histogram_interval.data)
                else:
                    histogram_size = HISTOGRAM_INTERVAL
                form2_status['is_histogram'] = True
                form2_status['refresh_page'] = True
                values = session['data_' + form2.function_name.data]
                x_axis_label = values['x_axis']
                histogram_values = values['values']
                max_pages = (len(histogram_values) + (PAGE_LENGTH - 1))  // PAGE_LENGTH
                end = current_page * PAGE_LENGTH
                begin = end - PAGE_LENGTH
                for h in histogram_values[begin:end]:
                    title = h[0]
                    values = h[1]
                    x_axis_size = h[2]
                    data += diagrams.histogram_diagram(values, title, histogram_size, x_axis_label, x_axis_size)

            previous_page, current_page, next_page = check_prev_next_pages(max_pages, current_page)
            form2_status['show'] = True
            form2_status['prev_page'] = (previous_page != 'None')
            form2_status['next_page'] = (next_page != 'None')
            form2_status['info'] = 'Page : ' + str(current_page) + '/' + str(max_pages)
            form2.prev_number.data = previous_page
            form2.current_number.data = current_page
            form2.next_number.data =  next_page
    return render_template("visu.html", display_page=display_page, form=form, form2=form2, form2_status=form2_status, data=data)