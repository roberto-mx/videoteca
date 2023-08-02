from django.shortcuts import render, redirect
from ..forms import ( 
    Descripcion,
    Mapa,
    Realizacion,
    Tecnicas,
    FormularioCombinado
)
from ..models import RegistroCalificacion, MaestroCintas
from django.core.paginator import Paginator
from django.db import transaction


from django.core.paginator import Paginator

def consultaFormulario(request):
    # Obtener todos los registros de la tabla RegistroCalificacion con estatusCalif igual a 'X' o 'I'
    calificaciones = RegistroCalificacion.objects.filter(estatusCalif__in=['P', 'R']).values(
        'id',
        'codigo_barras',
        'fecha_calificacion',
        'axo_produccion',
        'productor',
        'coordinador',
        'serie',
        'programa',
        'duracion',
        'guionista',
        'observaciones',
        'institucion_productora',   
        'fecha_modificacion',
        'estatusCalif',
    )

    # Configurar la paginación, no solo front
    paginator = Paginator(calificaciones, len(calificaciones))  # Mostrar todos los registros en una sola página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    consultaForm = {
        'formulario': page_obj
    }

    return render(request, 'calificaForm/consultaFormulario.html', consultaForm)

def datosGenerales(request):

    if request.method == 'POST':
        formulario = FormularioCombinado(request.POST)        
        if formulario.is_valid():
            # Extraer la fecha del formulario
            fecha_calificacion = formulario.cleaned_data['fecha_calificacion']
            try:

                fecha_calificacion_str = fecha_calificacion.strftime('%Y-%m-%d')

                # Crear un diccionario con los datos generales y guardar en la sesión
                datos_generales = {
                    'codigo_barras': formulario.cleaned_data['codigo_barras'],
                    'form_clave': formulario.cleaned_data['form_clave'].form_clave if formulario.cleaned_data['form_clave'] else None, #campos MaestroCintas
                    'tipo_id': formulario.cleaned_data['tipo_id'].tipo_id if formulario.cleaned_data['tipo_id'] else None, #campos MaestroCintas
                    'coordinador': formulario.cleaned_data['coordinador'],
                    'observaciones': formulario.cleaned_data['observaciones'],
                    'productor': formulario.cleaned_data['productor'],
                    'video_tipo': formulario.cleaned_data['video_tipo'].id_status if formulario.cleaned_data['video_tipo'] else None,
                    'origen_id': formulario.cleaned_data['origen_id'].origen_id if formulario.cleaned_data['origen_id'] else None, #campos MaestroCintas
                    'video_anoproduccion': formulario.cleaned_data['video_anoproduccion'], #campos MaestroCintas
                    'duracion': formulario.cleaned_data['duracion'],
                    'video_codificacion': formulario.cleaned_data['video_codificacion'], #campos MaestroCintas
                    'serie': formulario.cleaned_data['serie'],
                    'programa': formulario.cleaned_data['programa'],
                    'subtitulo_programa': formulario.cleaned_data['subtitulo_programa'],
                    'video_estatus': formulario.cleaned_data['video_estatus'], #campos MaestroCintas
                    'video_observaciones': formulario.cleaned_data['video_observaciones'],  # Agregado el campo de observaciones #campos MaestroCintas
                    'subtitserie': formulario.cleaned_data['subtitserie'],  # Agregado el campo de observaciones
                    'fecha_calificacion': fecha_calificacion_str,  # Almacenar la fecha como objeto datetime.date
                }

                # Guardar el diccionario de datos generales en la sesión solo si el formulario es válido
                request.session['datos_generales'] = datos_generales

                return redirect('descripcion')
            except ValueError:
                # Si la conversión de fecha falla, agregar un error personalizado al campo fecha_calificacion
                formulario.add_error('fecha_calificacion', 'Fecha inválida')

    else:
        # Inicializar el formulario con los datos almacenados en la sesión
        formulario = FormularioCombinado(initial=request.session.get('datos_generales'))

    return render(request, 'calificaForm/datosGenerales.html', {'formulario': formulario})

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
            tecnicas_data = form_tecnicas.cleaned_data

            # Obtener los datos de programas y series del formulario
            programas_series_data = {
                'programa': tecnicas_data.get('programa'),
                'serie': tecnicas_data.get('serie'),
                'subtitulo_programa': tecnicas_data.get('subtitulo_programa'),
                'subtitserie': tecnicas_data.get('subtitserie'),
            }

            try:
                with transaction.atomic():
                    # Crear una instancia de MaestroCintas con los datos combinados
                    maestro_cintas_instance = MaestroCintas(
                        video_cbarras=datos_generales.get('codigo_barras', ''),
                        tipo_id=datos_generales.get('tipo_id', ''),
                        form_clave=datos_generales.get('form_clave', ''),
                        video_tipo=datos_generales.get('video_tipo', ''),
                        origen_id=datos_generales.get('origen_id', ''),
                        video_anoproduccion=datos_generales.get('video_anoproduccion', ''),
                        video_estatus=datos_generales.get('video_estatus', ''),
                        video_codificacion=datos_generales.get('video_codificacion', ''),
                        video_observaciones=datos_generales.get('video_observaciones', ''),
                        # Campos de MaestroCintas
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
                        realizacion_data=realizacion_data,
                        estatusCalif='P'  # Establecer el valor de estatusCalif como 'P'
                        # Campos de RegistroCalificacion 
                    )
                    registro_calificacion_instance.save()

                    # Guardar los datos de programas y series en la sesión
                    request.session['programas_series_data'] = programas_series_data

                return redirect('calificaciones/consultaFormulario')
            except Exception as e:
                # Manejar el error de la transacción si es necesario
                print(str(e))
                # Puedes agregar un mensaje de error si deseas notificar al usuario sobre el problema
                return redirect('error_transaccion')
        else:
            # El formulario no es válido, puedes mostrar un mensaje de error si es necesario
            pass
    else:
        form_tecnicas = Tecnicas()

    return render(request, 'calificaForm/tecnicas.html', {'formulario': form_tecnicas})







