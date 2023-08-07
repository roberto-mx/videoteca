from django.shortcuts import render, redirect
from ..forms import ( 
    Descripcion,
    Mapa,
    Realizacion,
    Tecnicas,
    FormularioCombinado
)
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from ..models import RegistroCalificacion, MaestroCintas,CatStatus,TipoSerie, OrigenSerie
from django.core.paginator import Paginator
from django.db import transaction

def consultaFormulario(request):
    # Obtener todos los registros de la tabla RegistroCalificacion con estatusCalif igual a 'P' o 'R'
    calificaciones = RegistroCalificacion.objects.filter(estatusCalif__in=['P', 'R']).values(
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
        'fecha_modificacion',
        'estatusCalif',
        'calificador_modificacion',
    )

    consultaForm = {
        'formulario': calificaciones
    }

    return render(request, 'calificaForm/consultaFormulario.html', consultaForm)

@login_required
def datosGenerales(request):
    programasYSeries = request.session.get('programasYSeries', [])  # Recuperar la lista o usar una lista vacía por defecto

    if request.method == 'POST':
        formulario = FormularioCombinado(request.POST)
        if formulario.is_valid():
            # Extraer la fecha del formulario
            fecha_calificacion = formulario.cleaned_data['fecha_calificacion']
            try:
                fecha_calificacion_str = fecha_calificacion.strftime('%Y-%m-%d')
                programasYSeries.append({
                    'programa': formulario.cleaned_data['programa'],
                    'serie': formulario.cleaned_data['serie'],
                    'subtitulo_programa': formulario.cleaned_data['subtitulo_programa'],
                    'subtitserie': formulario.cleaned_data['subtitserie'],
                    # Agregar más campos si es necesario
                })

                # Crear un diccionario con los datos generales
                datos_generales = {
                    'codigo_barras': formulario.cleaned_data['codigo_barras'],
                    'form_clave': formulario.cleaned_data['form_clave'].form_clave if formulario.cleaned_data['form_clave'] else None,
                    'tipo_id': formulario.cleaned_data['tipo_id'].tipo_id if formulario.cleaned_data['tipo_id'] else None,
                    'coordinador': formulario.cleaned_data['coordinador'],
                    'observaciones': formulario.cleaned_data['observaciones'],
                    'productor': formulario.cleaned_data['productor'],
                    'video_tipo': formulario.cleaned_data['video_tipo'].id_status if formulario.cleaned_data['video_tipo'] else None,
                    'origen_id': formulario.cleaned_data['origen_id'].origen_id if formulario.cleaned_data['origen_id'] else None,
                    'video_anoproduccion': formulario.cleaned_data['video_anoproduccion'],
                    'duracion': formulario.cleaned_data['duracion'],
                    'video_codificacion': formulario.cleaned_data['video_codificacion'],
                    'serie': formulario.cleaned_data['serie'],
                    'programa': formulario.cleaned_data['programa'],
                    'subtitulo_programa': formulario.cleaned_data['subtitulo_programa'],
                    'video_estatus': formulario.cleaned_data['video_estatus'],
                    'video_observaciones': formulario.cleaned_data['video_observaciones'],
                    'subtitserie': formulario.cleaned_data['subtitserie'],
                    'fecha_calificacion': fecha_calificacion_str,
                }

                # Guardar los datos en la sesión
                request.session['datos_generales'] = datos_generales
                request.session['programasYSeries'] = programasYSeries

                return redirect('descripcion')
            except ValueError:
                formulario.add_error('fecha_calificacion', 'Fecha inválida')
    else:
        formulario = FormularioCombinado(initial=request.session.get('datos_generales'))
        programasYSeries = request.session.get('programasYSeries', [])

    return render(request, 'calificaForm/datosGenerales.html', {'formulario': formulario, 'programasYSeries': programasYSeries})

    
  
def descripcion(request):
    if request.method == 'POST':
        formulario = Descripcion(request.POST)
        if formulario.is_valid():
            request.session['descripcion_data'] = formulario.cleaned_data
            return redirect('mapa')
    else:
        formulario = Descripcion(initial=request.session.get('descripcion_data'))
    
    return render(request, 'calificaForm/descripcion.html', {'formulario': formulario})

def mapa(request):
    if request.method == 'POST':
        formulario = Mapa(request.POST)
        if formulario.is_valid():
            request.session['mapa_data'] = formulario.cleaned_data
            return redirect('realizacion')
    else:
        formulario = Mapa(initial=request.session.get('mapa_data'))
    
    return render(request, 'calificaForm/mapa.html', {'formulario': formulario})

def realizacion(request):
    if request.method == 'POST':
        formulario = Realizacion(request.POST)
        if formulario.is_valid():
            request.session['realizacion_data'] = formulario.cleaned_data
            return redirect('tecnicas')
    else:
        formulario = Realizacion(initial=request.session.get('realizacion_data'))
    
    return render(request, 'calificaForm/realizacion.html', {'formulario': formulario})

def tecnicas(request):
    if request.method == 'POST':
        form_tecnicas = Tecnicas(request.POST)

        if form_tecnicas.is_valid():
            # Obtener todos los datos de los formularios anteriores y del formulario actual
            datos_generales = request.session.get('datos_generales')
            descripcion_data = request.session.get('descripcion_data')
            mapa_data = request.session.get('mapa_data')
            realizacion_data = request.session.get('realizacion_data')

            id_status = datos_generales.get('id_status', '')
            tipo_id = datos_generales.get('tipo_id', '')
            origen_id = datos_generales.get('origen_id', '')


                # Buscar la instancia de CatStatus basada en el valor de id_status
            try:
                cat_status_instance = CatStatus.objects.get(id_status=id_status)
                tipo_id_instance = TipoSerie.objects.get(tipo_id=tipo_id)
                origen_id_instance = TipoSerie.objects.get(origen_id=origen_id)
            except CatStatus.DoesNotExist:
                # Manejar el caso si no se encuentra CatStatus con el id_status proporcionado
                cat_status_instance = None
                tipo_id_instance = None
                origen_id_instance = None
            
            with transaction.atomic():
                # Crear una instancia de MaestroCintas con los datos combinados
                maestro_cintas_instance = MaestroCintas(
                    video_cbarras=datos_generales.get('codigo_barras', ''),
                    tipo_id=tipo_id_instance,  # Asegúrate de definir tipo_id_instance correctamente
                    video_tipo=cat_status_instance,  # Asegúrate de definir cat_status_instance correctamente
                    origen_id=origen_id_instance,  # Asegúrate de definir origen_id_instance correctamente
                    video_anoproduccion=datos_generales.get('video_anoproduccion', ''),
                    video_estatus=datos_generales.get('video_estatus', ''),
                    video_codificacion=datos_generales.get('video_codificacion', ''),
                    video_observaciones=datos_generales.get('video_observaciones', ''),
                    # Otros campos de MaestroCintas
                )
                maestro_cintas_instance.save()

                # Crear una instancia de RegistroCalificacion y establecer la relación con MaestroCintas
                registro_calificacion_instance = RegistroCalificacion(
                    codigo_barras=maestro_cintas_instance,
                    coordinador=datos_generales.get('coordinador',''),
                    observaciones=datos_generales.get('observaciones',''),
                    productor=datos_generales.get('productor',''),
                    duracion=datos_generales.get('duracion',''),
                    serie=datos_generales.get('serie',''),
                    programa=datos_generales.get('programa',''),
                    subtitulo_programa=datos_generales.get('subtitulo_programa',''),
                    descripcion_data=descripcion_data,
                    mapa_data=mapa_data,
                    realizacion_data=realizacion_data
                    # Otros campos de RegistroCalificacion 
                )
                registro_calificacion_instance.save()

            # Eliminar los datos de la sesión
            del request.session['datos_generales']
            del request.session['descripcion_data']
            del request.session['mapa_data']
            del request.session['realizacion_data']

            return redirect('calificaciones/consultaFormulario')
        else:
            # El formulario no es válido, puedes mostrar un mensaje de error si es necesario
            print('Error en el formulario')
            pass
    else:
        form_tecnicas = Tecnicas()

    return render(request, 'calificaForm/tecnicas.html', {'formulario': form_tecnicas})






