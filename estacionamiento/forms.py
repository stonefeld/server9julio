from django import forms
from .models import RegistroEstacionamiento, AperturaManual, Proveedor


class EstacionamientoForm(forms.ModelForm):
    class Meta:
        model = RegistroEstacionamiento
        fields = [
            'identificador',
            'persona',
            'noSocio',
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


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'idProveedor',
            'nombre_proveedor'
        ]
