from django.shortcuts import render, redirect
from ..forms import FormularioCombinado, Descripcion, Mapa, Realizacion, Tecnicas, ModalForm
from ..models import MaestroCintas, RegistroCalificacion
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404



@csrf_exempt
def formulario(request):
    formulario_principal = FormularioCombinado()
    formulario_descripcion = Descripcion()
    formulario_mapa = Mapa()
    formulario_realizacion = Realizacion()
    formulario_tecnicas = Tecnicas()
    modal_form = ModalForm()

    if request.method == 'POST':
        formulario_principal = FormularioCombinado(request.POST)
        formulario_descripcion = Descripcion(request.POST)
        formulario_mapa = Mapa(request.POST)
        formulario_realizacion = Realizacion(request.POST)
        formulario_tecnicas = Tecnicas(request.POST)
        modal_form = ModalForm(request.POST)
        
        if formulario_principal.is_valid() and formulario_descripcion.is_valid() and formulario_mapa.is_valid() and formulario_realizacion.is_valid() and formulario_tecnicas.is_valid():
            # Obtener valores de los formularios
            datos_formulario_principal = formulario_principal.cleaned_data
            datos_formulario_descripcion = formulario_descripcion.cleaned_data
            datos_formulario_mapa = formulario_mapa.cleaned_data
            datos_formulario_tecnicas = formulario_tecnicas.cleaned_data
            datos_formulario_realizacion = formulario_realizacion.cleaned_data
            # datos_modal_form = modal_form.cleaned_data
            fecha_calificacion_actual = timezone.now().strftime('%Y-%m-%d')

            # Crear instancia de MaestroCintas
            nuevo_video_id = MaestroCintas.objects.aggregate(Max('video_id'))['video_id__max'] or 0
            nuevo_video_id += 1

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

            ano_produccion = maestro_cintas.video_anoproduccion

            # Datos del front-end-convertir json
            enviaForm = request.POST.get("programasYSeries")
            datos_modal_form = json.loads(enviaForm)
              
            for item in datos_modal_form:
                programa = item.get('programa')
                serie = item.get('serie')
                programaSubtitulo = item.get('programaSubtitulo')
                serieSubtitulo = item.get('serieSubtitulo')
                
                # Crear instancia de RegistroCalificacion para cada programa y serie
                registro_calificacion = RegistroCalificacion(
                    codigo_barras=maestro_cintas,  # Asignar la instancia de MaestroCintas
                    estatusCalif='P',
                    fecha_calificacion=fecha_calificacion_actual,  # Asignar la fecha actual
                    productor=datos_formulario_principal['productor'],
                    coordinador=datos_formulario_principal['coordinador'],
                    duracion=datos_formulario_principal['duracion'],
                    axo_produccion=ano_produccion,

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
                    #Obtengo los datos del objeto de el front
                    programa=programa,
                    serie=serie,
                    subtitulo_programa=programaSubtitulo,
                    subtitserie=serieSubtitulo,
                )
                registro_calificacion.save()

            response_data = {
                'message': 'Los datos se guardaron exitosamente.',
                'datos_modal_form': datos_modal_form  # Agrega los datos aquí 
            }
            return JsonResponse(response_data)

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

def consultaFormulario(request):
    # Obtener todos los registros de la tabla RegistroCalificacion con estatusCalif igual a 'P' o 'R'
    calificaciones = RegistroCalificacion.objects.filter(estatusCalif__in=['P', 'R']).order_by('-id').values(
        'id',
        'codigo_barras',  # Acceso a través de la relación
        'fecha_calificacion',
        'axo_produccion',
        'productor',
        'coordinador',
        'serie',
        'programa',
        'subtitulo_programa',
        'duracion',
        'guionista',
        'observaciones',
        'subtitserie',
        'estatusCalif',
        'tema',
        'eje_tematico',
        'institucion_productora',
        'derecho_patrimonial',
        'idioma_original',
        'elenco',
        'conductor',
        'locutor',
        'investigador',
        'tiempodur',
        'orientacion',
    )

    modal_form = ModalForm(request.POST or None)  # Inicializar el formulario

    if request.method == 'POST':
        # Aquí puedes manejar la lógica de guardado si es necesario
        pass  # Debes agregar tu lógica de guardado aquí

    consultaForm = {
        'formulario': calificaciones,
        'modal_form': modal_form,
    }

    return render(request, 'calificaForm/consultaFormulario.html', consultaForm)


# views.py
def editar(request, codigo_barras):
    try:
        maestro_cintas = MaestroCintas.objects.get(video_cbarras=codigo_barras)
        registro_calificaciones = RegistroCalificacion.objects.filter(codigo_barras=maestro_cintas)

        if request.method == 'POST':
            eliminar_id = request.POST.get('eliminar_id')  # Obtén el ID del programa a eliminar
            if eliminar_id is not None:
                try:
                    programa_a_eliminar = RegistroCalificacion.objects.get(id=eliminar_id)
                    programa_a_eliminar.delete()
                    # Redirige de nuevo a la página de edición después de eliminar
                    return redirect('editar', codigo_barras=codigo_barras)
                
                except RegistroCalificacion.DoesNotExist:
                    return HttpResponse("No se encontró el programa a eliminar.")

            # Resto de la lógica para procesar los formularios de edición
            formulario_principal = FormularioCombinado(request.POST)
            formulario_descripcion = Descripcion(request.POST, instance=registro_calificaciones[0])
            formulario_mapa = Mapa(request.POST, instance=registro_calificaciones[0])
            formulario_realizacion = Realizacion(request.POST, instance=registro_calificaciones[0])
            formulario_tecnicas = Tecnicas(request.POST, instance=registro_calificaciones[0])
            modal_form = ModalForm(request.POST)

            if formulario_principal.is_valid() and formulario_descripcion.is_valid() and formulario_mapa.is_valid() and formulario_realizacion.is_valid() and formulario_tecnicas.is_valid():
                # Guardar los cambios en los modelos
                formulario_principal.save()
                formulario_descripcion.save()
                formulario_mapa.save()
                formulario_realizacion.save()
                formulario_tecnicas.save()

                # Redirigir a la página de consulta o a donde desees después de la edición exitosa
                return redirect('editar')

        else:
            formulario_principal = FormularioCombinado(initial={
                'codigo_barras': maestro_cintas.video_cbarras,
                'form_clave': maestro_cintas.form_clave,
                'tipo_id': maestro_cintas.tipo_id,
                'video_tipo': maestro_cintas.video_tipo,
                'origen_id': maestro_cintas.origen_id,
                'video_observaciones': maestro_cintas.video_observaciones,
                'video_estatus': maestro_cintas.video_estatus,
                'video_codificacion': maestro_cintas.video_codificacion,
                'video_anoproduccion': maestro_cintas.video_anoproduccion,
                'fecha_calificacion': registro_calificaciones[0].fecha_calificacion,
                'productor': registro_calificaciones[0].productor,
                'coordinador': registro_calificaciones[0].coordinador,
                'duracion': registro_calificaciones[0].duracion,  # Agregamos la duración
            })

            # Obtener datos de la tabla de programas, creando un arreglo vacio para despues insertar ahi los datos
            programas_data = []  # Lista para almacenar los datos
            for registro in registro_calificaciones:
                programas_data.append({
                    'id': registro.id,
                    'programa': registro.programa,
                    'serie': registro.serie,
                    'programaSubtitulo': registro.subtitulo_programa,
                    'serieSubtitulo': registro.subtitserie,
                    'axo_produccion': registro.axo_produccion,
                    'duracion': registro.duracion,
                    'productor': registro.productor,
                    'coordinador': registro.coordinador,
                    'sinopsis': registro.sinopsis,
                    'participantes': registro.participantes,
                    'personajes': registro.personajes,
                })

            formulario_descripcion = Descripcion(instance=registro_calificaciones[0])
            formulario_mapa = Mapa(instance=registro_calificaciones[0])
            formulario_realizacion = Realizacion(instance=registro_calificaciones[0])
            formulario_tecnicas = Tecnicas(instance=registro_calificaciones[0])
            modal_form = ModalForm()

    except (MaestroCintas.DoesNotExist, RegistroCalificacion.DoesNotExist):
        # Manejar el caso cuando no se encuentra el objeto
        return HttpResponse("No se encontró el registro con el código de barras proporcionado.")

    return render(request, 'calificaForm/editar.html', {
        'formulario_principal': formulario_principal,
        'formulario_descripcion': formulario_descripcion,
        'formulario_mapa': formulario_mapa,
        'formulario_tecnicas': formulario_tecnicas,
        'formulario_realizacion': formulario_realizacion,
        'modal_form': modal_form,
        'programas_data': programas_data,
        'codigo_barras': codigo_barras,  # Agregamos los datos de la tabla de programas al contexto
    })




