from django import forms
from .models import EntradaGeneral, Persona


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = [
            'nombre',
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

