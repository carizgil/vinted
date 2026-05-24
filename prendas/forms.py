from django import forms
from .models import Prenda

class PrendaForm(forms.ModelForm):
    class Meta:
        model = Prenda
        fields = ['tipo_de_prenda', 'talla', 'color', 'marca', 'donde_esta_subido', 'precio_comprado', 'precio_vendido', 'estado']