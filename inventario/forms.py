from django import forms
from .models import MaestroCintas, DetalleProgramas, UsuariosVid, DetallePrestamos, Prestamos, RegistroCalificacion
from django.forms.models import inlineformset_factory

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
                  'video_tipo', 'video_fingreso', 'video_inventario', 'video_estatus',
                  'video_rack', 'video_nivel', 'video_anoproduccion', 'video_productor',
                  'video_coordinador', 'video_fechamov','video_observaciones', 'usua_clave',
                  'video_fchcal', 'video_target', 'tipo_id', 'origen_id']
        widgets = {
            'video_id': forms.HiddenInput(),
            'video_fechamov': forms.TextInput(),
            'video_cbarras': forms.TextInput(attrs={'placeholder': 'Código de barras'}),
            'video_observaciones': forms.Textarea(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['video_fechamov'].widget.attrs['value'] = datetime.datetime.now()

    video_usmov = forms.TypedChoiceField(
        coerce=lambda x: x == 1,
        choices=((0, 'No'), (1, 'Yes')),
        widget=forms.Select(attrs={'readonly': True})
    )

class Calificacion(forms.ModelForm):
    class Meta:
        model = RegistroCalificacion
        fields = ['serie','subtitulo_programa']
        # fields = '__all__'


class Identificacion(forms.ModelForm):
    class Meta:
        model = RegistroCalificacion
        fields = ['institucion_productora','codigo_original','codigo_orig1','codigo_submaster1','derecho_patrimonial']

class Mencion(forms.ModelForm):
    class Meta:
        model = RegistroCalificacion
        fields = ['institucion_productora','participantes']

class Contenido(forms.ModelForm):
    class Meta:
        model = RegistroCalificacion
        fields = ['institucion_productora','participantes']

class Versiones(forms.ModelForm):
    class Meta:
        model = RegistroCalificacion
        fields = ['institucion_productora','participantes']

class DescripcionTecnica(forms.ModelForm):
    class Meta:
        model = RegistroCalificacion
        fields = ['institucion_productora','participantes']

class AreaDisponibilidad(forms.ModelForm):
    class Meta:
        model = RegistroCalificacion
        fields = ['institucion_productora','participantes']

class AreaObservaciones(forms.ModelForm):
    class Meta:
        model = RegistroCalificacion
        fields = ['institucion_productora','participantes']

        

class DetalleProgramasForm(forms.ModelForm):
    class Meta:
        model = DetalleProgramas
        fields = ['vp_id', 'video_id', 'vp_serie', 'vp_subtitulo',#, 'video_cbarras'
            'vp_sinopsis', 'vp_participantes', 'vp_personajes', 'vp_areaconocimiento',
            'vp_asigmateria', 'vp_niveleducativo', 'vp_grado', 'vp_ejetematico',
            'vp_tema', 'vp_institproductora', 'vp_idiomaoriginal', 'vp_elenco',
            'vp_conductor', 'vp_locutor', 'vp_guionista', 'vp_investigador',
            'vp_derechopatrimonial', 'vp_fechacalificacion', 'vp_calificador',
            'vp_fecha_modificacion', 'vp_calificadormod', 'vp_sistema', 'vp_duracion',
            'vp_programa', 'vp_subtitserie', 'vp_orientacion', 'vp_duracionin',
            'vp_duracionout', 'vp_duracion1', 'tx', 'vp_observaciones', 'vp_fork',
            'vp_realizador', 'vp_musicao', 'vp_musicai', 'vp_cantante', 'vp_disquera',
            'vp_libreriam', 'vp_registro_obra']
        widgets = {
            'video_id': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(DetalleProgramasForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = UsuariosVid
        fields = '__all__'
   
class PrestamoForm(forms.ModelForm):
    pres_fecha_devolucion = forms.DateField(input_formats=['%d/%m/%Y'])
    class Meta:
        model = DetallePrestamos
        fields = '__all__'
        
PrestamoInlineFormset = inlineformset_factory(
    Prestamos,
    DetallePrestamos,
    form=PrestamoForm,
    extra=0,
    # max_num=5,
    # fk_name=None,
    # fields=None, exclude=None, can_order=False,
    # can_delete=True, max_num=None, formfield_callback=None,
    # widgets=None, validate_max=False, localized_fields=None,
    # labels=None, help_texts=None, error_messages=None,
    # min_num=None, validate_min=False, field_classes=None
)
    
    
