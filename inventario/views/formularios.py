from django.shortcuts import render, redirect
from ..forms import (
    FormularioCombinado,
    Mapa,
    FormularioCombinadoEditar,

)
from ..models import( 
    MaestroCintas, 
    RegistroCalificacion, 
    ProgramaSeries, 
    calificacionRegistro
)
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import JsonResponse
import json
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib import messages 
from django.db.utils import IntegrityError


def is_videote_user(user):
    if user: 
        return user.groups.filter(name='videotecaPermission').count() == 0
    return  False

@login_required
@csrf_exempt
def formulario(request):
    if not is_videote_user(request.user):
        messages.error(request, "Solo los de calificación pueden acceder a esta acción.")
        return redirect('prestamos_list')

    formulario_principal = FormularioCombinado()
    formulario_mapa = Mapa()

    if request.method == 'POST':
        formulario_principal = FormularioCombinado(request.POST)
        formulario_mapa = Mapa(request.POST)

        if formulario_principal.is_valid() and formulario_mapa.is_valid():
            try:
                datos_formulario_principal = formulario_principal.cleaned_data
                datos_formulario_mapa = formulario_mapa.cleaned_data
                fecha_calificacion_actual = timezone.now().strftime('%Y-%m-%d')

                nuevo_video_id = MaestroCintas.objects.aggregate(Max('video_id'))['video_id__max'] or 0
                nuevo_video_id += 1

                maestro_cintas = MaestroCintas(
                    video_id=nuevo_video_id,
                    video_cbarras=datos_formulario_principal['codigo_barras'],
                    video_anoproduccion=datos_formulario_principal['video_anoproduccion'],
                    form_clave=datos_formulario_principal['form_clave'],
                    tipo_id=datos_formulario_principal['tipo_id'],
                    video_tipo=datos_formulario_principal['video_tipo'],
                    video_estatus='En Calificación',
                    origen_id=datos_formulario_principal['origen_id'],
                )
                maestro_cintas.save()

                ano_produccion = maestro_cintas.video_anoproduccion

                registro_calificacion = calificacionRegistro(
                        codigo_barras=maestro_cintas,
                        fecha_calificacion=fecha_calificacion_actual,
                        aho_produccion=ano_produccion,
                        calificador=datos_formulario_principal['calificador'],
                        estatusCalif='En Calificación',
                        tema=datos_formulario_mapa['tema'],
                        areaConocimiento=datos_formulario_mapa['areaConocimiento'],
                        ejeTematico=datos_formulario_mapa['ejeTematico'],
                        nivelEducativo=datos_formulario_mapa['nivelEducativo'],
                        institucionProductora=datos_formulario_mapa['institucionProductora'],
                        asignaturaMateria=datos_formulario_mapa['asignaturaMateria'],
                )

                registro_calificacion.save()

                enviaForm = request.POST.get("programasYSeries")
                datos_modal_form = json.loads(enviaForm)

                for item in datos_modal_form:
                    programa = item.get('programa')
                    serie = item.get('serie')
                    subtituloPrograma = item.get('subtituloPrograma')
                    subtituloSerie = item.get('subtituloSerie')
                    sinopsis = item.get('sinopsis')
                    tiempoin = item.get('tiempoin')
                    tiempoout = item.get('tiempoout')
                    tiempodur = item.get('tiempodur')
                    observaciones = item.get('observaciones')
                    participantes = item.get('participantes')
                    personajes = item.get('personajes')
                    derechoPatrimonial = item.get('derechoPatrimonial')
                    orientacion = item.get('orientacion')
                    grado = item.get('grado')
                    idiomaOriginal = item.get('idiomaOriginal')
                    elenco = item.get('elenco')
                    conductor = item.get('conductor')
                    productor = item.get('productor')
                    investigador = item.get('investigador')

                    registro_programas = ProgramaSeries(
                        codigo_barras=maestro_cintas,
                        programa=programa,
                        serie=serie,
                        subtituloPrograma=subtituloPrograma,
                        subtituloSerie=subtituloSerie,
                        sinopsis=sinopsis,
                        tiempoin=tiempoin,
                        tiempoout=tiempoout,
                        tiempodur=tiempodur,
                        observaciones=observaciones,
                        participantes=participantes,
                        personajes=personajes,
                        derechoPatrimonial=derechoPatrimonial,
                        orientacion=orientacion,
                        grado=grado,
                        idiomaOriginal=idiomaOriginal,
                        elenco=elenco,
                        conductor=conductor,
                        productor=productor,
                        investigador=investigador
                    )
                    registro_programas.save()

                response_data = {
                    'message': 'Los datos se guardaron exitosamente.',
                    'datos_modal_form': datos_modal_form
                }
                return JsonResponse(response_data)
            except IntegrityError:
                response_data = {
                    'success': False,
                    'message': 'El código de barras ya existe.'
                }
                return JsonResponse(response_data)
        else:
            formulario_principal = FormularioCombinado()
            formulario_mapa = Mapa()

    return render(request, 'calificaForm/formulario.html', {
        'formulario_principal': formulario_principal,
        'formulario_mapa': formulario_mapa,
    })


def is_videoteca_user(user):
    if user: 
        return user.groups.filter(name='videotecaPermission').count() == 0
    return  False

@login_required
def consultaFormulario(request):
    if not is_videoteca_user(request.user):
        messages.error(request, "Solo los de calificación pueden acceder a esta acción.")
        return redirect('prestamos_list')  # Redirige al usuario a otra página

    calificaciones = calificacionRegistro.objects.filter(estatusCalif__in=['En Calificación', 'En Videoteca']).values(

    ).order_by('-id')
    

    programas_series = ProgramaSeries.objects.all()  # Obtén todos los datos de ProgramaSeries
    consultaForm = {'formulario': calificaciones, 'consulta': programas_series}  # Pasa ambos conjuntos de datos
   

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
        registro = get_object_or_404(calificacionRegistro, id=eliminar_id)
        registro.delete()
        return JsonResponse({'success': True})
    except calificacionRegistro.DoesNotExist:
        return JsonResponse({'success': False})
    
 
def agregarProgramaEdit(request, codigo_barras):
    try:
        maestro_cintas = MaestroCintas.objects.get(video_cbarras=codigo_barras)
        
        if request.method == 'POST':
            datos_modal_form = json.loads(request.body)
            print(datos_modal_form)
            for item in datos_modal_form:
                programa              = item.get('programa')
                serie                 = item.get('serie')
                subtituloPrograma     = item.get('subtituloPrograma')
                subtituloSerie        = item.get('subtituloSerie')
                sinopsis              = item.get('sinopsis')
                tiempoin              = item.get('tiempoin')
                tiempoout             = item.get('tiempoout')
                tiempodur             = item.get('tiempodur')
                observaciones         = item.get('observaciones')
                orientacion           = item.get('orientacion')
                derechoPatrimonial    = item.get('derechoPatrimonial')
                grado                 = item.get('grado')
                idiomaOriginal        = item.get('idiomaOriginal')
                elenco                = item.get('elenco')
                participantes         = item.get('participantes')
                personajes            = item.get('personajes')
                conductor             = item.get('conductor')
                productor             = item.get('productor')
                investigador          = item.get('investigador')
                
                programa_nuevo = ProgramaSeries(
                    codigo_barras=maestro_cintas,
                    programa=programa,
                    serie=serie,
                    subtituloPrograma=subtituloPrograma,
                    subtituloSerie=subtituloSerie,
                    sinopsis=sinopsis,
                    tiempoin=tiempoin,
                    tiempoout=tiempoout,
                    tiempodur=tiempodur,
                    observaciones=observaciones,
                    orientacion=orientacion,
                    derechoPatrimonial=derechoPatrimonial,
                    grado=grado,
                    idiomaOriginal=idiomaOriginal,
                    elenco=elenco,
                    participantes=participantes,
                    personajes=personajes,
                    conductor=conductor,
                    productor=productor,
                    investigador=investigador,
            
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
            if 'subtituloPrograma' in edited_data:
                programa_subtituloPrograma = edited_data['subtituloPrograma']
            if 'subtituloSerie' in edited_data:
                programa_subtituloSerie = edited_data['subtituloSerie']
            if 'sinopsis' in edited_data:
                sinopsis = edited_data['sinopsis']
            if 'tiempoin' in edited_data:
                tiempoin = edited_data['tiempoin']
            if 'tiempoout' in edited_data:
                tiempoout = edited_data['tiempoout']
            if 'tiempodur' in edited_data:
                tiempodur = edited_data['tiempodur']
            if 'observaciones' in edited_data:
                observaciones = edited_data['observaciones']
            if 'orientacion' in edited_data:
                orientacion = edited_data['orientacion']
            if 'derechoPatrimonial' in edited_data:
                derechoPatrimonial = edited_data['derechoPatrimonial']
            if 'grado' in edited_data:
                grado = edited_data['grado']
            if 'idiomaOriginal' in edited_data:
                idiomaOriginal = edited_data['idiomaOriginal']
            if 'elenco' in edited_data:
                elenco = edited_data['elenco']
            if 'participantes' in edited_data:
                participantes = edited_data['participantes']
            if 'personajes' in edited_data:
                personajes = edited_data['personajes']
            if 'conductor' in edited_data:
                conductor = edited_data['conductor']
            if 'productor' in edited_data:
                productor = edited_data['productor']
            if 'investigador' in edited_data:
                investigador = edited_data['investigador']

            programa.subtituloPrograma     = programa_subtituloPrograma
            programa.subtituloSerie        = programa_subtituloSerie
            programa.sinopsis              = sinopsis
            programa.tiempoin              = tiempoin
            programa.tiempoout             = tiempoout
            programa.tiempodur             = tiempodur
            programa.observaciones         = observaciones
            programa.orientacion           = orientacion
            programa.derechoPatrimonial    = derechoPatrimonial
            programa.grado                 = grado
            programa.idiomaOriginal        = idiomaOriginal
            programa.elenco                = elenco
            programa.participantes         = participantes
            programa.personajes            = personajes
            programa.conductor             = conductor
            programa.productor             = productor
            programa.investigador          = investigador
            
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
        registro_calificacion = calificacionRegistro.objects.get(id=id, codigo_barras=maestro_cintas)
        registro_programas = ProgramaSeries.objects.filter(codigo_barras=maestro_cintas)

        if request.method == 'POST':
            # Procesar el formulario personalizado de edición
            formulario_combinado = FormularioCombinadoEditar(request.POST)
            
            if formulario_combinado.is_valid():
                # Actualizar los datos en calificacionRegistro
                # registro_calificacion.codigo_barras = maestro_cintas.video_cbarras


                maestro_cintas.form_clave = formulario_combinado.cleaned_data['form_clave']
                maestro_cintas.tipo_id = formulario_combinado.cleaned_data['tipo_id']
                maestro_cintas.video_codificacion = formulario_combinado.cleaned_data['video_codificacion']
                maestro_cintas.video_tipo = formulario_combinado.cleaned_data['video_tipo']
                maestro_cintas.video_anoproduccion = formulario_combinado.cleaned_data['video_anoproduccion']
                maestro_cintas.origen_id = formulario_combinado.cleaned_data['origen_id']
                maestro_cintas.save()

                ano_produccion = maestro_cintas.video_anoproduccion
                registro_calificacion.codigo_barras = maestro_cintas
                registro_calificacion.fecha_calificacion = formulario_combinado.cleaned_data['fecha_calificacion']
                registro_calificacion.aho_produccion = ano_produccion
                registro_calificacion.calificador = formulario_combinado.cleaned_data['calificador']
                registro_calificacion.save()

                formulario_mapa = Mapa(request.POST, instance=registro_calificacion)

                if ( formulario_mapa.is_valid() ):
                    formulario_mapa.save()
                    return JsonResponse({'success': True, 'message': 'Cambios guardados exitosamente.'})
                else:
                    errors = {
                        'formulario_mapa': formulario_mapa.errors,

                    }
                    # print(errors)
                    return JsonResponse({'success': False, 'message': 'El formulario de mapa no es válido.', 'errors': errors})
            else:
                errors = {
                    'formulario_combinado': formulario_combinado.errors,
                }
                return JsonResponse({'success': False, 'message': 'El formulario combinado no es válido.', 'errors': errors})
        else:
            # Preparar los formularios con los datos actuales
            formulario_combinado = FormularioCombinadoEditar(initial={
                'registro_id'         : registro_calificacion.id,  
                'codigo_barras'       : registro_calificacion.codigo_barras,
                'fecha_calificacion'  : registro_calificacion.fecha_calificacion,
                'calificador'         : registro_calificacion.calificador,
            # --------------------------------------------------------------------
                'video_anoproduccion' : maestro_cintas.video_anoproduccion,
                'form_clave'          : maestro_cintas.form_clave,
                'tipo_id'             : maestro_cintas.tipo_id,
                'video_codificacion'  : maestro_cintas.video_codificacion,
                # 'video_observaciones' : maestro_cintas.video_observaciones,
                'video_tipo'          : maestro_cintas.video_tipo,
                'origen_id'           : maestro_cintas.origen_id,
            })

            for registro in registro_programas:
                programas_data.append({
                    'id': registro.id,
                    'codigo_barras':         registro.codigo_barras,
                    'programa':              registro.programa,
                    'serie':                 registro.serie,
                    'subtituloPrograma':     registro.subtituloPrograma,
                    'subtituloSerie':        registro.subtituloSerie,
                    'sinopsis':              registro.sinopsis,
                    'tiempoin':              registro.tiempoin,
                    'tiempoout':             registro.tiempoout,
                    'tiempodur':             registro.tiempodur,
                    'observaciones':         registro.observaciones,
                    'orientacion':           registro.orientacion,
                    'derechoPatrimonial':    registro.derechoPatrimonial,
                    'grado':                 registro.grado,
                    'idiomaOriginal':        registro.idiomaOriginal,
                    'elenco':                registro.elenco,
                    'participantes':         registro.participantes,
                    'personajes':            registro.personajes,
                    'conductor':             registro.conductor,
                    'productor':             registro.productor,
                    'investigador':          registro.investigador,
                })

            formulario_mapa = Mapa(instance=registro_calificacion)


            # Renderizar la página de edición con los formularios y datos
            return render(request, 'calificaForm/editar.html', {
                'formulario_combinado':     formulario_combinado,
                'formulario_mapa':          formulario_mapa,
                'programas_data':           programas_data,
            })

    except (calificacionRegistro.DoesNotExist, MaestroCintas.DoesNotExist, ProgramaSeries.DoesNotExist):
        # Manejar el caso cuando no se encuentra el objeto
        return JsonResponse({'error': "No se encontró el registro con el código de barras proporcionado."})

@csrf_exempt
def cambiarEstatusCalificacion(request, id):
    try:
        if request.method == 'POST':
            
            registro = calificacionRegistro.objects.get(pk=id)
            
            # Obtener el código de barras directamente desde la relación
            codigo_barras = registro.codigo_barras.video_cbarras

            # Actualizar el estatus en MaestroCintas
            maestro_cintas = MaestroCintas.objects.get(video_cbarras=codigo_barras)
            maestro_cintas.video_estatus = 'En Videoteca'
            maestro_cintas.save()

            # Actualizar el estatus en calificacionRegistro
            registro.estatusCalif = 'En Videoteca'
            registro.save()

            estatus_calif = registro.estatusCalif

        return JsonResponse({'success': True, 'message': "¡Calificado! Se ha cerrado la revisión.", 'estatusCalif': estatus_calif})
    except calificacionRegistro.DoesNotExist:
        return JsonResponse({'error': True, 'message': 'Ha ocurrido un error al realizar el cambio de estatus, favor de contactar al área de Desarrollo e Innovación.'})
