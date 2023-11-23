from django.shortcuts import render, redirect
from ..forms import (
    FormularioCombinado,
    Mapa,
    FormularioCombinadoEditar,
    # Descripcion,
    # Realizacion,
    # Tecnicas,
    # # ModalForm,
)
from ..models import MaestroCintas, RegistroCalificacion, ProgramaSeries
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
        return redirect('prestamos_list')  # Redirige al usuario a otra página

    formulario_principal = FormularioCombinado()
    formulario_mapa = Mapa()
    # modal_form = ModalForm()

    if request.method == 'POST':
        formulario_principal = FormularioCombinado(request.POST)
        formulario_mapa = Mapa(request.POST)

        # modal_form = ModalForm(request.POST)
        
        if formulario_principal.is_valid() and  formulario_mapa.is_valid() :
            # Obtener valores de los formularios
            datos_formulario_principal = formulario_principal.cleaned_data
            datos_formulario_mapa = formulario_mapa.cleaned_data
            # datos_modal_form = modal_form.cleaned_data
            fecha_calificacion_actual = timezone.now().strftime('%Y-%m-%d')
        
            # Crear instancia de MaestroCintas
            nuevo_video_id = MaestroCintas.objects.aggregate(Max('video_id'))['video_id__max'] or 0
            nuevo_video_id += 1

            maestro_cintas = MaestroCintas(
                video_id=nuevo_video_id,
                video_cbarras=datos_formulario_principal['codigo_barras'],
                video_anoproduccion=datos_formulario_principal['video_anoproduccion'],
                form_clave=datos_formulario_principal['form_clave'],
                tipo_id=datos_formulario_principal['tipo_id'],
                video_tipo=datos_formulario_principal['video_tipo'],
                origen_id=datos_formulario_principal['origen_id'],
                
            )
            maestro_cintas.save()

            ano_produccion = maestro_cintas.video_anoproduccion

            # Datos del front-end-convertir json
            enviaForm = request.POST.get("programasYSeries")
            datos_modal_form = json.loads(enviaForm)
              
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
                #----------------------------------------------------------------
                participantes         = item.get('participantes')    
                personajes            = item.get('personajes')    
                derechoPatrimonial    = item.get('derechoPatrimonial')    
                orientacion           = item.get('orientacion')    
                grado                 = item.get('grado')    
                idiomaOriginal        = item.get('idiomaOriginal')   
                #----------------------------------------------------------------
                elenco                = item.get('elenco') 
                conductor             = item.get('conductor') 
                productor             = item.get('productor') 
                investigador          = item.get('investigador') 
                      
                  
                
                # Crear instancia de RegistroCalificacion para cada programa y serie
                registro_calificacion = RegistroCalificacion(
                    codigo_barras=maestro_cintas,  # Asignar la instancia de MaestroCintas
                    estatusCalif='P',
                    fecha_calificacion=fecha_calificacion_actual,  # Asignar la fecha actual
                    # productor=datos_formulario_principal['productor'],
                    axo_produccion=ano_produccion,

                    # Form Mapa
                    tema=datos_formulario_mapa['tema'],
                    areaConocimiento=datos_formulario_mapa['areaConocimiento'],
                    ejeTematico=datos_formulario_mapa['ejeTematico'],
                    nivelEducativo=datos_formulario_mapa['nivelEducativo'],
                    institucionProductora=datos_formulario_mapa['institucionProductora'],
                    asignaturaMateria=datos_formulario_mapa['asignaturaMateria'],
                    
                )
                
                registro_calificacion.save()

                registro_programas = ProgramaSeries(
                    codigo_barras         =  maestro_cintas,
                    programa              =  programa,
                    serie                 =  serie,
                    subtituloPrograma     =  subtituloPrograma,
                    subtituloSerie        =  subtituloSerie,
                    sinopsis              =  sinopsis,
                    tiempoin              =  tiempoin,
                    tiempoout             =  tiempoout,
                    tiempodur             =  tiempodur,
                    observaciones         =  observaciones,
                    #----------------------------------------------------------------
                    participantes         =  participantes,
                    personajes            =  personajes,
                    derechoPatrimonial    =  derechoPatrimonial,
                    orientacion           =  orientacion,
                    grado                 =  grado,
                    idiomaOriginal        =  idiomaOriginal,
                    #----------------------------------
                    elenco                = elenco,
                    conductor             = conductor,
                    productor             = productor,
                    investigador          = investigador
                )
                registro_programas.save()

            response_data = {
                'message': 'Los datos se guardaron exitosamente.',
                'datos_modal_form': datos_modal_form  # Agrega los datos aquí 
            }
            return JsonResponse(response_data)

        else:
            
            formulario_principal = FormularioCombinado()
            formulario_mapa = Mapa()
            # modal_form = ModalForm()

    return render(request, 'calificaForm/formulario.html', {
        'formulario_principal': formulario_principal,
        'formulario_mapa': formulario_mapa,
        # 'modal_form': modal_form,
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

    calificaciones = RegistroCalificacion.objects.filter(estatusCalif__in=['P', 'R']).values(
        # ... (tu consulta)
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
                programa              = item.get('programa')
                serie                 = item.get('serie')
                subtituloPrograma     = item.get('subtituloPrograma')
                subtituloSerie        = item.get('subtituloSerie')
                sinopsis              = item.get('sinopsis')
                tiempoin              = item.get('tiempoin')
                tiempoout             = item.get('tiempoout')
                tiempodur             = item.get('tiempodur')
                observaciones = item.get('observaciones')
                
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
             
            programa.subtituloPrograma    = programa_subtituloPrograma
            programa.subtituloSerie       = programa_subtituloSerie
            programa.sinopsis              = sinopsis
            programa.tiempoin              = tiempoin
            programa.tiempoout             = tiempoout
            programa.tiempodur             = tiempodur
            programa.observaciones = observaciones
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
                maestro_cintas.video_estatus = formulario_combinado.cleaned_data['video_estatus']
                maestro_cintas.video_observaciones = formulario_combinado.cleaned_data['video_observaciones']
                maestro_cintas.origen_id = formulario_combinado.cleaned_data['origen_id']
                maestro_cintas.video_tipo = formulario_combinado.cleaned_data['video_tipo']
                maestro_cintas.form_clave = formulario_combinado.cleaned_data['form_clave']
                maestro_cintas.tipo_id = formulario_combinado.cleaned_data['tipo_id']

                 # Cambiar el valor de estatusCalif de 'P' a 'R'
                # registro_calificacion.estatusCalif = 'R' esto ser == a Videoteca
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
                'registro_id':          registro_calificacion.id,  
                'codigo_barras':        registro_calificacion.codigo_barras,
                'fecha_calificacion':   registro_calificacion.fecha_calificacion,
                'productor':            registro_calificacion.productor,
                'coordinador':          registro_calificacion.coordinador,
                'video_anoproduccion':  maestro_cintas.video_anoproduccion,
                'video_estatus':        maestro_cintas.video_estatus,
                'video_observaciones':  maestro_cintas.video_observaciones,
                'origen_id':            maestro_cintas.origen_id,
                'video_tipo':           maestro_cintas.video_tipo,
                'form_clave':           maestro_cintas.form_clave,
                'tipo_id':              maestro_cintas.tipo_id,
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
                    'observaciones': registro.observaciones
                })

            formulario_descripcion = Descripcion(instance=registro_calificacion)
            formulario_mapa = Mapa(instance=registro_calificacion)
            formulario_tecnicas = Tecnicas(instance=registro_calificacion)
            formulario_realizacion = Realizacion(instance=registro_calificacion)

            # Renderizar la página de edición con los formularios y datos
            return render(request, 'calificaForm/editar.html', {
                'formulario_combinado':     formulario_combinado,
                'formulario_descripcion':   formulario_descripcion,
                'formulario_mapa':          formulario_mapa,
                'formulario_tecnicas':      formulario_tecnicas,
                'formulario_realizacion':   formulario_realizacion,
                'codigo_barras':            codigo_barras,
                'programas_data':           programas_data,
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