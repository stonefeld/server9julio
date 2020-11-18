from django import forms
from django.forms import ModelForm

from .models import EntradaGeneral

class RegistroEntradaGeneralForms(ModelForm):
    lugar = forms.CharField()
    tiempo = forms.DateTimeField()

    class Meta:
        model = EntradaGeneral
        fields = ['persona', 'lugar', 'tiempo']
