from flask import (
    Blueprint, render_template, session, send_file
)
from flaskr.forms import VisuForm
from . import getter, diagrams

bp = Blueprint('visualise', __name__, url_prefix='')

@bp.route('/visu', methods=('GET', 'POST'))
def register_visu():
    form = VisuForm()
    data = ''
    display_page = getter.statements_in_session()
    if display_page and form.validate_on_submit():
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
        else:
            raise ValueError("Ce type de retour n'est pas défini: " + return_type)
    return render_template("visu.html", display_page=display_page, form=form, data=data)