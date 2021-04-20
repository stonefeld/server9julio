from django import forms
from .models import RegistroEstacionamiento, AperturaManual


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
        ]

class AperturaManualForm(forms.ModelForm):
    class Meta:
        model = AperturaManual
        fields = [
            'razon',
            'comentario',
            'direccion',
        ]
