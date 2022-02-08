from django import forms

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


class MaestrosCintasForm(forms.Form):
    id = forms.HiddenInput()
    cbarras = forms.CharField(label="Código de barras", max_length=12)
    formato = forms.ChoiceField(label="Formato")
    idproduccion = forms.IntegerField(label="Id producción")
    codificacion = forms.CharField(label="Formato de la cinta", max_length=20)
    tipo = forms.ChoiceField(label='Tipo de video')
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

    def __init__(self, *args, **kwargs):
        super(MaestrosCintasForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'