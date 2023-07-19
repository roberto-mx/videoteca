from django.shortcuts import render, redirect
from ..forms import Generales, Descripcion, Mapa, Realizacion, Tecnicas
from ..models import RegistroCalificacion
from django.core.paginator import Paginator
from django.contrib import messages
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
        formulario = Generales(request.POST)
        if formulario.is_valid():
            # Obtener el valor del campo fecha_calificacion del formulario
            fecha_calificacion = formulario.cleaned_data['fecha_calificacion']
            
            try:
                # Convertir el valor de fecha_calificacion a una cadena en el formato deseado
                fecha_calificacion_str = fecha_calificacion.strftime('%Y-%m-%d')
                
                # Asignar la cadena de fecha al campo fecha_calificacion en los datos del formulario
                formulario.cleaned_data['fecha_calificacion'] = fecha_calificacion_str
                
                # Guardar los datos en la sesión
                request.session['datos_generales'] = formulario.cleaned_data
                
                return redirect('descripcion')
            except ValueError:
                # Si la conversión de fecha falla, agregar un error personalizado al campo fecha_calificacion
                formulario.add_error('fecha_calificacion', 'Fecha inválida')
    else:
        formulario = Generales(initial=request.session.get('datos_generales'))
    
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
        # Obtener los datos del formulario
        datos_generales = request.session.get('datos_generales')
        descripcion_data = request.session.get('descripcion_data')
        mapa_data = request.session.get('mapa_data')
        realizacion_data = request.session.get('realizacion_data')
        tecnicas_data = request.POST
        
        # Crear instancias de los formularios con los datos actualizados
        form_datos_generales = Generales(data=datos_generales)
        form_descripcion = Descripcion(data=descripcion_data)
        form_mapa = Mapa(data=mapa_data)
        form_realizacion = Realizacion(data=realizacion_data)
        form_tecnicas = Tecnicas(data=tecnicas_data)
        
        # Verificar si los formularios son válidos
        if (
            form_datos_generales.is_valid() and
            form_descripcion.is_valid() and
            form_mapa.is_valid() and
            form_realizacion.is_valid() and
            form_tecnicas.is_valid()
        ):
            # Crear una instancia del modelo RegistroCalificacion
            registro = RegistroCalificacion()
            
            # Asignar los valores de los campos del modelo con los datos de los formularios
            registro.codigo_barras = form_datos_generales.cleaned_data['codigo_barras']
            registro.fecha_calificacion = form_datos_generales.cleaned_data['fecha_calificacion']
            registro.axo_produccion = form_datos_generales.cleaned_data['axo_produccion']
            registro.productor = form_datos_generales.cleaned_data['productor']
            registro.coordinador = form_datos_generales.cleaned_data['coordinador']
            registro.observaciones = form_datos_generales.cleaned_data['observaciones']
            registro.serie = form_datos_generales.cleaned_data['serie']
            registro.duracion = form_datos_generales.cleaned_data['duracion']
            registro.subtitserie = form_datos_generales.cleaned_data['subtitserie']
            registro.programa = form_datos_generales.cleaned_data['programa']
            registro.subtitulo_programa = form_datos_generales.cleaned_data['subtitulo_programa']
            
            # Form de descripción
            registro.sinopsis = form_descripcion.cleaned_data['sinopsis']
            registro.tiempodur = form_descripcion.cleaned_data['tiempodur']
            registro.participantes = form_descripcion.cleaned_data['participantes']
            registro.personajes = form_descripcion.cleaned_data['personajes']
            registro.derecho_patrimonial = form_descripcion.cleaned_data['derecho_patrimonial']
            registro.asignatura_materia = form_descripcion.cleaned_data['asignatura_materia']
            registro.grado = form_descripcion.cleaned_data['grado']
            registro.orientacion = form_descripcion.cleaned_data['orientacion']
            #Form de mapa
            registro.area_de_conocimiento = form_mapa.cleaned_data['area_de_conocimiento']
            registro.eje_tematico = form_mapa.cleaned_data['eje_tematico']
            registro.nivel_educativo = form_mapa.cleaned_data['nivel_educativo']
            registro.tema = form_mapa.cleaned_data['tema']
            #Form de realización
            registro.guionista = form_realizacion.cleaned_data['guionista']
            registro.locutor = form_realizacion.cleaned_data['locutor']
            registro.investigador = form_realizacion.cleaned_data['investigador']
            registro.elenco = form_realizacion.cleaned_data['elenco']
            registro.conductor = form_realizacion.cleaned_data['conductor']
            registro.institucion_productora = form_realizacion.cleaned_data['institucion_productora']
            registro.estatusCalif = 'P'  # Colocar  estatusCalif  'P'
            #Form de técnicas
            registro.participantes = form_tecnicas.cleaned_data['idioma_original']
            # Guardar el registro en la base de datos
            registro.save()
            # Limpiar los datos de la sesión
            del request.session['datos_generales']
            del request.session['descripcion_data']
            del request.session['mapa_data']
            del request.session['realizacion_data']
            
            # Redireccionar a la vista deseada
            if(registro.save()):

                return redirect('calificaciones/consultaFormulario')
    else:
        form_tecnicas = Tecnicas()
    
    return render(request, 'calificaForm/tecnicas.html', {'formulario': form_tecnicas})

def editar(request, id):
    registro = RegistroCalificacion.objects.get(id=id)
    formulario = Generales(request.POST or None, request.FILES or None, instance=registro)
    formulario2 = Descripcion(request.POST or None, request.FILES or None, instance=registro)
    formulario3 = Mapa(request.POST or None, request.FILES or None, instance=registro)
    formulario4 = Realizacion(request.POST or None, request.FILES or None, instance=registro)
    formulario5 = Tecnicas(request.POST or None, request.FILES or None, instance=registro)

    if request.method == 'POST':
        # Si se presionó el botón "Guardar para revisión"
        if 'guardar_btn' in request.POST:
            if formulario.is_valid() and formulario2.is_valid() and formulario3.is_valid() and formulario4.is_valid() and formulario5.is_valid():
                registro = formulario.save(commit=False)
                registro.estatusCalif = 'P'  # Guardado para revisión
                registro.save()
                return render(request, 'calificaForm/editar.html',
                              {
                                  'formulario': formulario,
                                  'formulario2': formulario2,
                                  'formulario3': formulario3,
                                  'formulario4': formulario4,
                                  'formulario5': formulario5,
                                  'guardado_para_revision': True
                              })

        # Si se presionó el botón "Revisado y Aceptado"
        if 'aceptaForm' in request.POST:
            if formulario.is_valid() and formulario2.is_valid() and formulario3.is_valid() and formulario4.is_valid() and formulario5.is_valid():
                registro = formulario.save(commit=False)
                registro.estatusCalif = 'R'  # Revisado y Aceptado
                registro.save()
                return render(request, 'calificaForm/editar.html',
                              {
                                  'formulario': formulario,
                                  'formulario2': formulario2,
                                  'formulario3': formulario3,
                                  'formulario4': formulario4,
                                  'formulario5': formulario5,
                                  'revisado_y_aceptado': True
                              })

    return render(request, 'calificaForm/editar.html',
                  {
                      'formulario': formulario,
                      'formulario2': formulario2,
                      'formulario3': formulario3,
                      'formulario4': formulario4,
                      'formulario5': formulario5
                  })



