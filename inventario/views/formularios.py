from django.shortcuts import render, redirect
from ..forms import FormularioCombinado, Descripcion, Mapa, Realizacion, Tecnicas, ModalForm
from ..models import MaestroCintas, RegistroCalificacion
from django.utils import timezone

def formulario(request):
    if request.method == 'POST':
        formulario_principal = FormularioCombinado(request.POST)
        formulario_descripcion = Descripcion(request.POST)
        formulario_mapa = Mapa(request.POST)
        formulario_realizacion = Realizacion(request.POST)
        formulario_tecnicas = Tecnicas(request.POST)
        modal_form = ModalForm(request.POST)
        
        if formulario_realizacion.is_valid():
            # Procesar los datos del formulario principal
            datos_formulario_principal = formulario_principal.cleaned_data
            
            # Obtener valores de los otros formularios
            datos_formulario_descripcion = formulario_descripcion.cleaned_data
            datos_formulario_mapa = formulario_mapa.cleaned_data
            datos_formulario_tecnicas = formulario_tecnicas.cleaned_data
            datos_formulario_realizacion = formulario_realizacion.cleaned_data
            datos_modal_form = modal_form.cleaned_data  

            fecha_calificacion_actual = timezone.now().strftime('%Y-%m-%d')

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
                # Agregar otros campos aquí si son necesarios
            )
            maestro_cintas.save()
            
            # Crear objeto RegistroCalificacion
            registro_calificacion = RegistroCalificacion(
                codigo_barras=datos_formulario_principal['codigo_barras'],
                fecha_calificacion=fecha_calificacion_actual,  # Asignar la fecha actual
                productor=datos_formulario_principal['productor'],
                coordinador=datos_formulario_principal['coordinador'],
                duracion=datos_formulario_principal['duracion'],

                # Form Descripción
                sinopsis=datos_formulario_descripcion['sinopsis'],
                tiempodur=datos_formulario_descripcion['tiempodur'],
                participantes=datos_formulario_descripcion['participantes'],
                personajes=datos_formulario_descripcion['personajes'],
                derecho_patrimonial=datos_formulario_descripcion['derecho_patrimonial'],
                asignatura_materia=datos_formulario_descripcion['asignatura_materia'],
                grado=datos_formulario_descripcion['grado'],
                orientacion=datos_formulario_descripcion['orientacion'],

                # Form Mapa
                area_de_conocimiento=datos_formulario_mapa['area_de_conocimiento'],
                eje_tematico=datos_formulario_mapa['eje_tematico'],
                nivel_educativo=datos_formulario_mapa['nivel_educativo'],
                tema=datos_formulario_mapa['tema'],

                #Form Técnicas
                idioma_original=datos_formulario_tecnicas['idioma_original'],
                observaciones=datos_formulario_tecnicas['observaciones'],

                # Form Realización
                guionista=datos_formulario_realizacion['guionista'],
                locutor=datos_formulario_realizacion['locutor'],
                investigador=datos_formulario_realizacion['investigador'],
                elenco=datos_formulario_realizacion['elenco'],
                conductor=datos_formulario_realizacion['conductor'],
                institucion_productora=datos_formulario_realizacion['institucion_productora'],

                # Form Modal
                serie=datos_modal_form['serie'],
                programa=datos_modal_form['programa'],
                subtitulo_programa=datos_modal_form['subtitulo_programa'],
                subtitserie=datos_modal_form['subtitserie']
                # ... otros campos ...
                # Agregar campos de los otros formularios aquí
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
