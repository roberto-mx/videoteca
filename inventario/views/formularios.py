from django.shortcuts import render, redirect
from ..forms import FormularioCombinado, Descripcion, Mapa, Realizacion, Tecnicas, ModalForm
from ..models import MaestroCintas, RegistroCalificacion

def formulario(request):
    if request.method == 'POST':
        formulario_principal = FormularioCombinado(request.POST)
        formulario_descripcion = Descripcion(request.POST)
        formulario_mapa = Mapa(request.POST)
        formulario_realizacion = Realizacion(request.POST)
        formulario_tecnicas = Tecnicas(request.POST)
        
        if (formulario_principal.is_valid() and formulario_descripcion.is_valid() and
            formulario_mapa.is_valid() and formulario_realizacion.is_valid() and formulario_tecnicas.is_valid()):
            
            # Procesar los datos del formulario principal
            datos_formulario_principal = formulario_principal.cleaned_data
            fecha_calificacion = datos_formulario_principal['fecha_calificacion']
            fecha_calificacion_str = fecha_calificacion.strftime('%Y-%m-%d')
            
            # Inserción en MaestroCintas
            maestro_cintas = MaestroCintas(
                video_cbarras=datos_formulario_principal['codigo_barras'],
                form_clave=datos_formulario_principal['form_clave'],
                tipo_id=datos_formulario_principal['tipo_id'],
                video_tipo=datos_formulario_principal['video_tipo'],
                origen_id=datos_formulario_principal['origen_id'],
                video_observaciones=datos_formulario_principal['video_observaciones'],
                video_estatus=datos_formulario_principal['video_estatus'],
                video_codificacion=datos_formulario_principal['video_codificacion'],
                video_anoproduccion=datos_formulario_principal['video_anoproduccion'],
            )
            maestro_cintas.save()
            
            # Inserción en RegistroCalificacion
            registro_calificacion = RegistroCalificacion(
                codigo_barras=datos_formulario_principal['codigo_barras'],
                fecha_calificacion=datos_formulario_principal['fecha_calificacion'],
                productor=datos_formulario_principal['productor'],
                coordinador=datos_formulario_principal['coordinador'],
                duracion=datos_formulario_principal['duracion'],
                observaciones=datos_formulario_principal['observaciones'],
                # ... otros campos ...
            )
            registro_calificacion.save()
            
            # Redirigir o realizar otra acción si es necesario
            return redirect('calificaciones/consultaFormulario')
            
    else:
        formulario_principal = FormularioCombinado()
        formulario_descripcion = Descripcion()
        formulario_mapa = Mapa()
        formulario_tecnicas = Tecnicas()
        formulario_realizacion = Realizacion()
        modal_form = ModalForm()

    return render(request, 'calificaForm/formulario.html', {
        'formulario_principal': formulario_principal,
        'formulario_descripcion': formulario_descripcion,
        'formulario_mapa': formulario_mapa,
        'formulario_tecnicas': formulario_tecnicas,
        'formulario_realizacion': formulario_realizacion,
        'modal_form': modal_form,
    })
