from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, RadioField, BooleanField, TextAreaField, HiddenField
from .visualize_list import visu_list

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
    choices = []
    for visu in visu_list:
        choices.append((visu.name, visu.name))
    radio = RadioField('Visu', choices=choices)
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
    choices = []
    for visu in visu_list:
        choices.append((visu.name, visu.name))
    prev_page = SubmitField('Prev page')
    prev_number = HiddenField('Prev number')
    function_name = HiddenField('Function name')
    return_type = HiddenField('Return type')
    histogram_interval = StringField('Taille intervalle de l\'histogramme:')
    next_page = SubmitField('Next page')
    next_number = HiddenField('Next number')
    current_page_status = 'OK'

    def get_visu_fun(self,selected_visu):
        for visu in visu_list:
            if selected_visu == visu.name:
                return visu.function
        raise ValueError("L'option sélectionnée n'existe pas dans la liste des visualisations visu_list")
    


class DevForm(FlaskForm):
    dev_text = TextAreaField('Saisie dev')
    submit = SubmitField('Traiter')
