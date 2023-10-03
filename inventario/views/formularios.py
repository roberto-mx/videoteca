from django.shortcuts import render, redirect
from ..forms import FormularioCombinado, Descripcion, Mapa, Realizacion, Tecnicas, ModalForm, FormularioCombinadoEditar, ModalFormEdit
from ..models import MaestroCintas, RegistroCalificacion, ProgramaSeries
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import JsonResponse
import json
from django.utils import timezone
# from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib import messages 


def is_videote_user(user):
    if user: 
        return user.groups.filter(name='videotecaPermission').count() == 0
    return  False

@login_required
@csrf_exempt
def formulario(request):
    if not is_videote_user(request.user):
        messages.error(request, "Solo los de calificación pueden acceder a esta acción.")
        return redirect('prestamos_list')  # Redirige al usuario a otra página

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
                )
                registro_calificacion.save()

                registro_programas = ProgramaSeries(
                    codigo_barras=maestro_cintas,
                    programa=programa,
                    serie=serie,
                    subtitulo_programa=programaSubtitulo,
                    subtitulo_serie=serieSubtitulo,
                )
                registro_programas.save()

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
    # Obtener registros únicos por código de barras con estatusCalif igual a 'P' o 'R'
    calificaciones = RegistroCalificacion.objects.filter(estatusCalif__in=['P', 'R']).values(
        'codigo_barras'
    ).annotate(
        id=Max('id'),  # Obtén el ID máximo para cada código de barras
        duracion=Max('duracion'),  # Obtén la duración máxima para cada código de barras
        observaciones=Max('observaciones'),  # Obtén las observaciones máximas para cada código de barras
        institucion_productora=Max('institucion_productora'),  # Obtén la institución productora máxima para cada código de barras
        fecha_calificacion=Max('fecha_calificacion'),  # Obtén la fecha de calificación máxima para cada código de barras
        estatusCalif=Max('estatusCalif')  # Obtén el estatus de calificación máximo para cada código de barras
    ).order_by('-id')

    consultaForm = {'formulario': calificaciones}

    return render(request, 'calificaForm/consultaFormulario.html', consultaForm)

def eliminarProgramaSerie(request, id):
    id = request.POST.get('eliminar_id')
    try:
        registro = ProgramaSeries.objects.get(id=id)
        registro.delete()
        return JsonResponse({'success': True})
    except ProgramaSeries.DoesNotExist:
        return JsonResponse({'success': False})
    
def eliminarRegistro(request, id):
    eliminar_id = request.POST.get('eliminar_id')
    try:
        registro = get_object_or_404(RegistroCalificacion, id=eliminar_id)
        registro.delete()
        return JsonResponse({'success': True})
    except RegistroCalificacion.DoesNotExist:
        return JsonResponse({'success': False})
    
 
def agregarProgramaEdit(request, codigo_barras):
    try:
        maestro_cintas = MaestroCintas.objects.get(video_cbarras=codigo_barras)
        
        if request.method == 'POST':
            datos_modal_form = json.loads(request.body)
            
            for item in datos_modal_form:
                programa = item.get('programa')
                serie = item.get('serie')
                programaSubtitulo = item.get('programaSubtitulo')
                serieSubtitulo = item.get('serieSubtitulo')
                
                programa_nuevo = ProgramaSeries(
                    codigo_barras=maestro_cintas,
                    programa=programa,
                    serie=serie,
                    subtitulo_programa=programaSubtitulo,
                    subtitulo_serie=serieSubtitulo,
                )
                programa_nuevo.save()

                nuevo_id = programa_nuevo.id

            response_data = {
                'success': True,
                'message': 'Los programas se agregaron exitosamente.',
                'nuevo_id': nuevo_id,
                'datos_modal_form': datos_modal_form
            }
        else:
            response_data = {
                'success': False,
                'message': 'Método no permitido.',
            }
    except MaestroCintas.DoesNotExist:
        response_data = {
            'success': False,
            'message': 'No se encontró el código de barras proporcionado.',
        }
    
    return JsonResponse(response_data)

def editar_programa(request, programa_id):
    try:
        programa = ProgramaSeries.objects.get(id=programa_id)
        if request.method == 'POST':
            #Se obtienen los datos del front con json.loads(request.body)
            edited_data = json.loads(request.body)['edited_data']
     
            # Actualizar los campos que deben ser editados
            programa.programa = edited_data['programa']
            programa.serie = edited_data['serie']
            
            # Actualizar solo si los campos existen en edited_data
            if 'programaSubtitulo' in edited_data:
                programa_subtitulo_programa = edited_data['programaSubtitulo']
            if 'serieSubtitulo' in edited_data:
                programa_subtitulo_serie = edited_data['serieSubtitulo']
            
            programa.subtitulo_programa = programa_subtitulo_programa
            programa.subtitulo_serie = programa_subtitulo_serie
            
            programa.save()
            
            return JsonResponse({'success': True, 'message': 'Cambios guardados exitosamente.'})
        else:
            errors = programa.errors
            return JsonResponse({'success': False, 'message': 'El formulario no es válido.', 'errors': errors})
    except ProgramaSeries.DoesNotExist:
        return JsonResponse({'error': 'No se encontró el programa proporcionado.'})
    
@csrf_exempt
def editar(request, id, codigo_barras):
    programas_data = []
    
    try:
        # Obtener el registro de calificación y el maestro de cintas asociado
        maestro_cintas = MaestroCintas.objects.get(video_cbarras=codigo_barras)
        registro_calificacion = RegistroCalificacion.objects.get(id=id, codigo_barras=maestro_cintas)
        registro_programas = ProgramaSeries.objects.filter(codigo_barras=maestro_cintas)

        if request.method == 'POST':

            # Procesar el formulario personalizado de edición
            formulario_combinado = FormularioCombinadoEditar(request.POST)
            
            if formulario_combinado.is_valid():
                # Actualizar los datos en RegistroCalificacion
                registro_calificacion.codigo_barras = maestro_cintas.video_cbarras
                registro_calificacion.fecha_calificacion = formulario_combinado.cleaned_data['fecha_calificacion']
                registro_calificacion.productor = formulario_combinado.cleaned_data['productor']
                registro_calificacion.coordinador = formulario_combinado.cleaned_data['coordinador']
                maestro_cintas.video_anoproduccion = formulario_combinado.cleaned_data['video_anoproduccion']
                registro_calificacion.duracion = formulario_combinado.cleaned_data['duracion']
                maestro_cintas.video_codificacion = formulario_combinado.cleaned_data['video_codificacion']
                maestro_cintas.video_estatus = formulario_combinado.cleaned_data['video_estatus']
                maestro_cintas.video_observaciones = formulario_combinado.cleaned_data['video_observaciones']
                maestro_cintas.origen_id = formulario_combinado.cleaned_data['origen_id']
                maestro_cintas.video_tipo = formulario_combinado.cleaned_data['video_tipo']
                maestro_cintas.form_clave = formulario_combinado.cleaned_data['form_clave']
                maestro_cintas.tipo_id = formulario_combinado.cleaned_data['tipo_id']

                 # Cambiar el valor de estatusCalif de 'P' a 'R'
                #registro_calificacion.estatusCalif = 'R'
                # Actualizar otros campos si es necesario
                registro_calificacion.save()
                maestro_cintas.save()

                # Procesar los demás formularios y guardar los cambios en los modelos relacionados
                formulario_descripcion = Descripcion(request.POST, instance=registro_calificacion)
                formulario_mapa = Mapa(request.POST, instance=registro_calificacion)
                formulario_tecnicas = Tecnicas(request.POST, instance=registro_calificacion)
                formulario_realizacion = Realizacion(request.POST, instance=registro_calificacion)
                
                if (formulario_descripcion.is_valid() and formulario_mapa.is_valid() and
                    formulario_tecnicas.is_valid() and formulario_realizacion.is_valid()):
                    formulario_descripcion.save()#
                    formulario_mapa.save()
                    formulario_tecnicas.save()
                    formulario_realizacion.save()
                    return JsonResponse({'success': True, 'message': 'Cambios guardados exitosamente.'})
                else:
                    errors = {
                        'formulario_descripcion': formulario_descripcion.errors,
                        'formulario_mapa': formulario_mapa.errors,
                        'formulario_tecnicas': formulario_tecnicas.errors,
                        'formulario_realizacion': formulario_realizacion.errors,
                    }
                    return JsonResponse({'success': False, 'message': 'El formulario no es válido.', 'errors': errors})
            else:
                errors = {
                    'formulario_combinado': formulario_combinado.errors,
                }
                return JsonResponse({'success': False, 'message': 'El formulario no es válido.', 'errors': errors})
        else:
            # Preparar los formularios con los datos actuales
            formulario_combinado = FormularioCombinadoEditar(initial={
                'registro_id': registro_calificacion.id,  
                'codigo_barras': registro_calificacion.codigo_barras,
                'fecha_calificacion': registro_calificacion.fecha_calificacion,
                'productor': registro_calificacion.productor,
                'coordinador': registro_calificacion.coordinador,
                'video_anoproduccion': maestro_cintas.video_anoproduccion,
                'duracion': registro_calificacion.duracion,
                'video_codificacion': maestro_cintas.video_codificacion,
                'video_estatus': maestro_cintas.video_estatus,
                'video_observaciones': maestro_cintas.video_observaciones,
                'origen_id': maestro_cintas.origen_id,
                'video_tipo': maestro_cintas.video_tipo,
                'form_clave': maestro_cintas.form_clave,
                'tipo_id': maestro_cintas.tipo_id,
            })

            for registro in registro_programas:
                programas_data.append({
                    'id': registro.id,
                    'codigo_barras': registro.codigo_barras,
                    'programa': registro.programa,
                    'serie': registro.serie,
                    'programaSubtitulo': registro.subtitulo_programa,
                    'serieSubtitulo': registro.subtitulo_serie,
                })

            formulario_descripcion = Descripcion(instance=registro_calificacion)
            formulario_mapa = Mapa(instance=registro_calificacion)
            formulario_tecnicas = Tecnicas(instance=registro_calificacion)
            formulario_realizacion = Realizacion(instance=registro_calificacion)

            # Renderizar la página de edición con los formularios y datos
            return render(request, 'calificaForm/editar.html', {
                'formulario_combinado': formulario_combinado,
                'formulario_descripcion': formulario_descripcion,
                'formulario_mapa': formulario_mapa,
                'formulario_tecnicas': formulario_tecnicas,
                'formulario_realizacion': formulario_realizacion,
                'codigo_barras': codigo_barras,
                'programas_data': programas_data,
            })

    except (RegistroCalificacion.DoesNotExist, MaestroCintas.DoesNotExist, ProgramaSeries.DoesNotExist):
        # Manejar el caso cuando no se encuentra el objeto
        return JsonResponse({'error': "No se encontró el registro con el código de barras proporcionado."})

@csrf_exempt
def cambiarEstatusCalificacion(request, id):
    try:
        if request.method == 'POST':
            registro = RegistroCalificacion.objects.get(pk=id)
            # Cambiar el valor de estatusCalif de 'P' a 'R'
            registro.estatusCalif = 'R'
            registro.save()

            estatus_calif = registro.estatusCalif

        return JsonResponse({'success': True, 'message': "¡Calificado! Se a cerrado la revición.",'estatusCalif': estatus_calif})  # Cambia 'pagina_de_exito' al nombre de tu página de éxito
    except RegistroCalificacion.DoesNotExist:
        return JsonResponse({'error': True, 'message': 'A ocurrido un error al realizar el cambio de estatus, favor de contactar al área de Desarrollo e Innovación.'})