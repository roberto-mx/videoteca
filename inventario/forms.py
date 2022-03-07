from django import forms
from .models import MaestroCintas

import datetime

class Login(forms.Form):
    usuario = forms.CharField(label='Usuario', max_length=100)
    pwd = forms.CharField(label='Contraseña', max_length=100)


class FormatosCintasForm(forms.Form):
    clave = forms.CharField()
    descripcion = forms.CharField(widget=forms.Textarea)
    form_duracion = forms.CharField()
    form_prefijo = forms.CharField()
    
    def send_email(self):
        pass


class MaestroCintasFilter(forms.Form):
    cbarras = forms.CharField(label="Código de barras", max_length=12)
    formato = forms.ChoiceField(label="Formato")
    tipo = forms.ChoiceField(label='Tipo de video')
    estatus = forms.CharField(label="Estatus de la cinta", max_length=20)
    year = forms.IntegerField(label="Año de registro")

    def qs(request_get, queryset):
        cbarras = request_get['q']
        if cbarras == '':
            return queryset
        return MaestroCintas.objects.filter(video_cbarras=cbarras)

class MaestrosCintasForm(forms.ModelForm):
    class Meta:
        model = MaestroCintas
        fields = ['video_id', 'video_cbarras', 'form_clave', 'video_codificacion', 
            'video_codificacion', 'video_tipo', 'video_fingreso', 'video_inventario',
            'video_estatus', 'video_rack', 'video_nivel', 'video_anoproduccion',
            'video_idproductor', 'video_productor', 'video_idcoordinador', 
            'video_coordinador', 'video_usmov', 'video_fechamov', 'video_observaciones',
            'usua_clave', 'video_fchcal', 'video_target', 'tipo_id', 'origen_id']
        widgets = {
            'video_id': forms.HiddenInput(),
            'video_fechamov': forms.HiddenInput(attrs={'value':datetime.datetime.now()}),
            'video_cbarras': forms.TextInput(attrs={'placeholder': 'Código de barras'}),
        }


    """
    video_id = forms.CharField(widget=forms.HiddenInput())
    video_cbarras = forms.CharField(
        label="Código de barras",
        max_length=12,
        widget=forms.TextInput(attrs={'placeholder': 'Código de barras'})
    )
    form_clave = forms.ChoiceField(label="Formato de la cinta")
    idproduccion = forms.IntegerField(label="Id producción")
    video_codificacion = forms.CharField(label="Formato de la cinta", max_length=20)
    video_tipo = forms.ChoiceField(label='Tipo de video')
    fingreso = forms.DateField(label="Fecha ingreso")
    inventario = forms.CharField(label="Inventario", max_length=4)
    estatus = forms.CharField(label="Estatus de la cinta", max_length=20)
    rack = forms.CharField(label="Rack", max_length=4)
    nivel = forms.CharField(label="Nivel", max_length=4)
    anoproduccion = forms.IntegerField(label="Año de producción")
    idproductor = forms.IntegerField(label="Id de productor")
    productor = forms.CharField(label="Productor", max_length=100)
    idcoordinador = forms.IntegerField(label="Id de coordinador")
    coordinador = forms.CharField(label="Coordinador", max_length=80)
    usmov = forms.IntegerField(label="usmov")
    fechamov = forms.DateTimeField(label="Fecha de movimiento")
    observaciones = forms.CharField(label="Observaciones", max_length=300, widget=forms.Textarea)
    usua_clave = forms.CharField(label="Clave", max_length=12)
    fchcal = forms.DateField(label="Fecha de calificación")
    target = forms.CharField(label="Target", max_length=45)
    tipo_id = forms.ChoiceField(label="Tipo de Serie")
    origen_id = forms.ChoiceField(label="Origen de serie")
    """

    def __init__(self, *args, **kwargs):
        super(MaestrosCintasForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
