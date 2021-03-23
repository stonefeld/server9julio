from django import forms
from .models import RegistroEstacionamiento


class EstacionamientoForm(forms.ModelForm):
    class Meta:
        model = RegistroEstacionamiento
        fields = [
            'identificador',
            'tipo',
            'lugar',
            'tiempo',
            'direccion',
            'autorizado',
            'cicloCaja',
            'cicloMensual'
        ]
