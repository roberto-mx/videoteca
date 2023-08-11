from django.shortcuts import render, redirect
from ..forms import FormularioCombinado, Descripcion, Mapa, Realizacion, Tecnicas, ModalForm
from ..models import MaestroCintas, RegistroCalificacion
from django.db.models import Max
from django.utils import timezone

def formulario(request):
    programasYSeries = request.session.get('programasYSeries', []) 
    if request.method == 'POST':
        formulario_principal = FormularioCombinado(request.POST)
        formulario_descripcion = Descripcion(request.POST)
        formulario_mapa = Mapa(request.POST)
        formulario_realizacion = Realizacion(request.POST)
        formulario_tecnicas = Tecnicas(request.POST)
        modal_form = ModalForm(request.POST)
        
        if formulario_principal.is_valid() and formulario_descripcion.is_valid() and formulario_mapa.is_valid() and formulario_realizacion.is_valid() and formulario_tecnicas.is_valid() and modal_form.is_valid():
            datos_formulario_principal = formulario_principal.cleaned_data
            # Obtener valores de los formularios
            datos_formulario_descripcion = formulario_descripcion.cleaned_data
            datos_formulario_mapa = formulario_mapa.cleaned_data
            datos_formulario_tecnicas = formulario_tecnicas.cleaned_data
            datos_modal_form = modal_form.cleaned_data  
            datos_formulario_realizacion = formulario_realizacion.cleaned_data

            fecha_calificacion_actual = timezone.now().strftime('%Y-%m-%d')
            programasYSeries.append({
                'programa': datos_modal_form['programa'],
                'serie': datos_modal_form['serie'],
                'subtitulo_programa': datos_modal_form['subtitulo_programa'],
                'subtitserie': datos_modal_form['subtitserie'],
                # Agregar más campos si es necesario
            })

             # Obtener el último valor de video_id
            ultimo_video_id = MaestroCintas.objects.aggregate(Max('video_id'))['video_id__max']
            if ultimo_video_id is None:
                nuevo_video_id = 1
            else:
                nuevo_video_id = ultimo_video_id + 1

            maestro_cintas = MaestroCintas(
                video_id=nuevo_video_id,
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

            # Crear objeto RegistroCalificacion
            registro_calificacion = RegistroCalificacion(
                codigo_barras=maestro_cintas,  # Asignar la instancia de MaestroCintas
                estatusCalif='P',
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

                # Form Técnicas
                idioma_original=datos_formulario_tecnicas['idioma_original'],
                observaciones=datos_formulario_tecnicas['observaciones'],

                # Form Realización
                guionista=datos_formulario_realizacion['guionista'],
                locutor=datos_formulario_realizacion['locutor'],
                investigador=datos_formulario_realizacion['investigador'],
                elenco=datos_formulario_realizacion['elenco'],
                conductor=datos_formulario_realizacion['conductor'],
                institucion_productora=datos_formulario_realizacion['institucion_productora'],

                # Form Modal (programas y series)
                programa=datos_modal_form['programa'],
                serie=datos_modal_form['serie'],
                subtitulo_programa=datos_modal_form['subtitulo_programa'],
                subtitserie=datos_modal_form['subtitserie']
            )

            request.session['programasYSeries'] = programasYSeries
            registro_calificacion.save()

            # Redirigir o realizar otra acción si es necesario
            return redirect('consultaFormulario')
            
    else:
        formulario_principal = FormularioCombinado()
        formulario_descripcion = Descripcion()
        formulario_mapa = Mapa()
        formulario_tecnicas = Tecnicas()
        formulario_realizacion = Realizacion()
        modal_form = ModalForm()
        programasYSeries = request.session.get('programasYSeries', [])

    return render(request, 'calificaForm/formulario.html', {
        'formulario_principal': formulario_principal,
        'formulario_descripcion': formulario_descripcion,
        'formulario_mapa': formulario_mapa,
        'formulario_tecnicas': formulario_tecnicas,
        'formulario_realizacion': formulario_realizacion,
        'modal_form': modal_form,
        'programasYSeries': programasYSeries
    })

