from django import forms
from .models import  Persona
from registroGeneral.models import  EntradaGeneral


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = [
            'nombre_apellido',
            'dni',
            'nrSocio',
            'nrTarjeta',
        ]

class RegistroUsuario(forms.ModelForm):
    lugar = forms.CharField()
    tiempo = forms.DateTimeField()

    class Meta:
        model = EntradaGeneral
        fields = ['persona', 'lugar', 'tiempo']

