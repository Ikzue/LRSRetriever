from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, RadioField, BooleanField, TextAreaField

class RetrieveForm(FlaskForm):
    number_list = StringField('Numéros étudiant')
    hash_list = StringField('Hashs étudiant')
    date = SelectField('Date', choices=[('today', "Aujourd'hui"), ('week', 'Cette semaine'), ('month', 'Ce mois'),
    ('all', 'Tout')])
    submit = SubmitField('Envoi')

class LogsForm(FlaskForm):
    radio = RadioField('Logs', choices=[('chrono', "Chronologique"), ('session', 'Par session')])
    submit = SubmitField('Afficher')
    interaction = BooleanField('Interactions logicielles', default='checked')
    execution = BooleanField('Execution programme/Evaluation interpréteur', default='checked')
    errors = BooleanField('Erreurs exec/eval', default='checked')
    states = BooleanField('Changement d\'états', default='checked')
    editor = BooleanField('Saisie editeur', default='checked')
    extensions = BooleanField('Extensions', default='checked')
    number_list = StringField('Numéros étudiant')
    hash_list = StringField('Hashs étudiant')
    session_id = StringField('IDs session')


class VisuForm(FlaskForm):
    radio = RadioField('Visu', choices=[('stats', "Statistiques"), ('keywords', 'Mots clés'), ('execution', 'Nombre exécutions'), \
        ('errors', 'Types d\'erreurs'), ('instructions', 'Types d\'instructions saisies')])
    submit = SubmitField('Afficher')


class DevForm(FlaskForm):
    dev_text = TextAreaField('Saisie dev')
    submit = SubmitField('Traiter')
