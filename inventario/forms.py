from django import forms

class Login(forms.Form):
    usuario = forms.CharField(label='Usuario', max_length=100)
    pwd = forms.CharField(label='Contraseña', max_length=100)