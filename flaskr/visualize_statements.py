from flask import (
    Blueprint, render_template, session, send_file, request
)
from flaskr.forms import VisuForm, VisuPrevSuivForm
from . import getter, diagrams
import ast

bp = Blueprint('visualise', __name__, url_prefix='')

@bp.route('/visu', methods=('GET', 'POST'))
def register_visu():
    form = VisuForm()
    form2 = VisuPrevSuivForm()
    show_form2 = {'show' : False, 'prev_page' : False, 'next_page' : False}
    data = ''
    display_page = getter.statements_in_session()
    if display_page:
        if form.submit.data and form.validate():
            return_type, function = form.get_visu_fun(form.radio.data)
            hashes = getter.get_hashes(form.number_list.data, form.hash_list.data)
            session_ids = getter.get_session_ids(form.session_id.data)
            filters = {'hashes' : hashes, 'session-ids' : session_ids}
            print(filters)
            
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
            elif return_type == 'multiple_page_HTML':
                previous_page, next_page, data = function(session['statements'], filters)
                function_name = form.radio.data
                form2 = VisuPrevSuivForm(function_name=function_name, prev_number=previous_page, next_number=next_page,
                hashes=hashes, session_ids=session_ids)
                show_form2['show'] = True
                show_form2['prev_page'] = (previous_page != 'None')
                show_form2['next_page'] = (next_page != 'None')
            else:
                raise ValueError("Ce type de retour n'est pas défini: " + return_type)
        elif (form2.prev_page.data or form2.next_page.data) and form2.validate():
            if form2.prev_page.data:
                current_page = int(form2.prev_number.data)
            elif form2.next_page.data:
                current_page = int(form2.next_number.data)
            function = form2.get_visu_fun(form2.function_name.data)
            hashes = ast.literal_eval(form2.hashes.data)
            session_ids = ast.literal_eval(form2.session_ids.data)
            filters = {'hashes' : hashes, 'session-ids' : session_ids}
            previous_page, next_page, data = function(session['statements'], filters, current_page)
            show_form2['show'] = True
            show_form2['prev_page'] = (previous_page != 'None')
            show_form2['next_page'] = (next_page != 'None')
            form2.prev_number.data = previous_page
            form2.next_number.data =  next_page
    return render_template("visu.html", display_page=display_page, form=form, form2=form2, show_form2=show_form2, data=data)