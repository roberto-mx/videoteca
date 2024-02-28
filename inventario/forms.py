from django import forms
from .models import (
        MaestroCintas,
        DetalleProgramas,
        UsuariosVid,
        DetallePrestamos,
        Prestamos,
        RegistroCalificacion,
        FormatosCintas,
        CatStatus,
        TipoSerie,
        OrigenSerie,
        calificacionRegistro,
        ProgramaSeries
)

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
        fields = [ 'video_cbarras', 'form_clave', 'video_codificacion',
                  'video_tipo', 'video_fingreso', 'video_inventario', 'video_estatus',
                  'video_rack', 'video_nivel', 'video_anoproduccion', 'video_productor',
                  'video_coordinador', 'video_fechamov','video_observaciones', 'usua_clave',
                  'video_fchcal', 'video_target', 'tipo_id', 'origen_id']
        widgets = {
            # 'video_id': forms.HiddenInput(),
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
    

class FormularioCombinado(forms.Form):
    codigo_barras = forms.CharField(max_length=12, widget=forms.TextInput(attrs={'placeholder': 'Código de barras'}), required=False)
    fecha_calificacion = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False) 
    video_anoproduccion = forms.CharField(max_length=10, label="Año de producción", required=False)
    form_clave = forms.ModelChoiceField(queryset=FormatosCintas.objects.all(), widget=forms.Select(attrs={'class': 'mi-clase-css'}), required=False)
    tipo_id = forms.ModelChoiceField(queryset=TipoSerie.objects.all(), widget=forms.Select(attrs={'class': 'mi-clase-css'}), required=False)
    video_codificacion = forms.CharField(max_length=20, required=True)
    video_tipo = forms.ModelChoiceField(queryset=CatStatus.objects.all(), widget=forms.Select(attrs={'class': 'mi-clase-css'}), required=False)
    origen_id = forms.ModelChoiceField(queryset=OrigenSerie.objects.all(), widget=forms.Select(attrs={'class': 'mi-clase-css'}), required=False)
    calificador = forms.CharField(max_length=80, required=False)
    widgets = {
            'fecha_calificacion': forms.DateInput(attrs={'type': 'date'}),
            'video_id': forms.HiddenInput(),
    }

class Mapa(forms.ModelForm):
    class Meta:
        model = calificacionRegistro
        fields = [
            'tema',
            'areaConocimiento',
            'ejeTematico',
            'nivelEducativo',
            'institucionProductora',
            'asignaturaMateria',
        ]



    
class FormularioCombinadoEditar(forms.Form):
    registro_id = forms.IntegerField(widget=forms.HiddenInput()) 
    codigo_barras = forms.CharField(max_length=12, widget=forms.TextInput(attrs={'placeholder': 'Código de barras'}), required=False)
    fecha_calificacion = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False) 
    video_anoproduccion = forms.CharField(max_length=10, label="Año de producción", required=False)
    form_clave = forms.ModelChoiceField(queryset=FormatosCintas.objects.all(), widget=forms.Select(attrs={'class': 'mi-clase-css'}), required=False)
    tipo_id = forms.ModelChoiceField(queryset=TipoSerie.objects.all(), widget=forms.Select(attrs={'class': 'mi-clase-css'}), required=False)
    video_codificacion = forms.CharField(max_length=20, required=False)
    video_tipo = forms.ModelChoiceField(queryset=CatStatus.objects.all(), widget=forms.Select(attrs={'class': 'mi-clase-css'}), required=False)
    origen_id = forms.ModelChoiceField(queryset=OrigenSerie.objects.all(), widget=forms.Select(attrs={'class': 'mi-clase-css'}), required=False)
    calificador = forms.CharField(max_length=80, required=False)
    widgets = {
            'fecha_calificacion': forms.DateInput(attrs={'type': 'date'}),
            'video_id': forms.HiddenInput(),
    }


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
    
    
