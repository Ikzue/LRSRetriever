from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, RadioField, BooleanField, TextAreaField, HiddenField
from .visualize_list import visu_list

class RetrieveForm(FlaskForm):
    # A form used to retrieve statements
    number_list = StringField('Numéros étudiant')
    hash_list = StringField('Hashs étudiant')
    date = SelectField('Date', choices=[('today', "Aujourd'hui"), ('week', 'Cette semaine'), ('month', 'Ce mois'),
    ('all', 'Tout')])
    submit = SubmitField('Envoi')

class LogsForm(FlaskForm):
    # A form used to show logs from retrieved statements
    radio = RadioField('Logs', choices=[('chrono', "Chronologique"), ('session', 'Par session')], default='chrono')
    submit = SubmitField('Afficher')
    interaction = BooleanField('Interactions logicielles', default='checked')
    execution = BooleanField('Execution programme/Evaluation interpréteur', default='checked')
    errors = BooleanField('Erreurs exec/eval', default='checked')
    states = BooleanField('Changement d\'états', default='checked')
    editor = BooleanField('Saisie editeur', default='checked')
    extensions = BooleanField('Extensions')
    number_list = StringField('Numéros étudiant')
    hash_list = StringField('Hashs étudiant')
    session_id = StringField('IDs session')


class VisuForm(FlaskForm):
    # A form used to show visualisations from retrieved statements
    choices = []
    for visu in visu_list:
        choices.append((visu.name, visu.name))
    radio = RadioField('Visu', choices=choices, default=choices[0][0])
    number_list = StringField('Numéros étudiant')
    hash_list = StringField('Hashs étudiant')
    session_id = StringField('IDs session')
    submit = SubmitField('Afficher')

    def get_visu_fun(self,selected_visu):
        for visu in visu_list:
            if selected_visu == visu.name:
                return (visu.return_type, visu.function)
        raise ValueError("L'option sélectionnée n'existe pas dans la liste des visualisations visu_list")

class VisuPrevSuivForm(FlaskForm):
    # A form used in the "Visualisations" webpage to manage multiple pages of visualisations.
    choices = []
    for visu in visu_list:
        choices.append((visu.name, visu.name))
    prev_page = SubmitField('Prev page')
    prev_number = HiddenField('Prev number')
    refresh_page = SubmitField('Refresh')
    current_number = HiddenField('Prev number')
    function_name = HiddenField('Function name')
    return_type = HiddenField('Return type')
    histogram_interval = StringField('Taille de l\'intervalle:')
    next_page = SubmitField('Next page')
    next_number = HiddenField('Next number')
    current_page_status = 'OK'

    def get_visu_fun(self,selected_visu):
        for visu in visu_list:
            if selected_visu == visu.name:
                return visu.function
        raise ValueError("L'option sélectionnée n'existe pas dans la liste des visualisations visu_list")
    


class DevForm(FlaskForm):
    # A form used to manage the user's commands in the 'Console dev (legacy)' webpage.
    dev_text = TextAreaField('Saisie dev')
    submit = SubmitField('Traiter')
