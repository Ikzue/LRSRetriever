from flask import Blueprint, render_template

bp = Blueprint('tutorial', __name__, url_prefix='')

@bp.route('/tuto', methods=('GET', 'POST'))
def register():
    return render_template('tutorial.html')
