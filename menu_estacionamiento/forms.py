#menu_estacionamiento/forms.py
from django.forms import ModelForm, DateInput
from menu_estacionamiento.models import Tarifa_mod
from django import forms

class TarifaForm(ModelForm):
  class Meta:
    model = Tarifa_mod
    # datetime-local is a HTML5 input type, format to make date time show on fields
    widgets = {
      'start_time': DateInput(attrs={'type': 'datetime-local', 'placeholder' : 'Año-Mes-Dia Hora:Min'}, format='%Y-%m-%d %H:%M'),
      'end_time': DateInput(attrs={'type': 'datetime-local', 'placeholder' : 'Año-Mes-Dia Hora:Min'}, format='%Y-%m-%d %H:%M'),
    }
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super(TarifaForm, self).__init__(*args, **kwargs)
    # input_formats to parse HTML5 datetime-local input to datetime field
    self.fields['start_time'].input_formats = ('%Y-%m-%d %H:%M',)
    self.fields['end_time'].input_formats = ('%Y-%m-%d %H:%M',)
