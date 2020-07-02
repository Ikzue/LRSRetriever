from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, RadioField

class RetrieveForm(FlaskForm):
    student_hash = StringField('Hash étudiant')
    date = SelectField('Date', choices=[('today', "Aujourd'hui"), ('week', 'Cette semaine'), ('month', 'Ce mois'),
    ('all', 'Tout')])
    submit = SubmitField('Envoi')

class LogsForm(FlaskForm):
    radio = RadioField('Visu', choices=[('chrono', "Chronologique"), ('session', 'Par session')])
    submit = SubmitField('Afficher')