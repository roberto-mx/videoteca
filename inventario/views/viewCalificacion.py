from django.shortcuts import render, redirect
from ..forms import Generales, Descripcion, Mapa, Realizacion, Tecnicas
from ..models import RegistroCalificacion
from django.core.paginator import Paginator


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
        'calificador_modificacion',
        'fecha_modificacion',
        'estatusCalif',
    )

    # Configurar la paginación
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
        
        # Actualizar los datos con los campos del formulario actual
        datos_generales.update(descripcion_data)
        datos_generales.update(mapa_data)
        datos_generales.update(realizacion_data)
        datos_generales.update(tecnicas_data)
        
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
            
            # Asignar otros valores de los campos según corresponda
            registro.sinopsis = form_descripcion.cleaned_data['sinopsis']
            registro.tiempodur = form_descripcion.cleaned_data['tiempodur']
            registro.participantes = form_descripcion.cleaned_data['participantes']
            registro.personajes = form_descripcion.cleaned_data['personajes']
            registro.derecho_patrimonial = form_descripcion.cleaned_data['derecho_patrimonial']
            registro.asignatura_materia = form_descripcion.cleaned_data['asignatura_materia']
            registro.grado = form_descripcion.cleaned_data['grado']
            registro.orientacion = form_descripcion.cleaned_data['orientacion']
            registro.area_de_conocimiento = form_mapa.cleaned_data['area_de_conocimiento']
            registro.eje_tematico = form_mapa.cleaned_data['eje_tematico']
            registro.nivel_educativo = form_mapa.cleaned_data['nivel_educativo']
            registro.tema = form_mapa.cleaned_data['tema']
            registro.guionista = form_realizacion.cleaned_data['guionista']
            registro.locutor = form_realizacion.cleaned_data['locutor']
            registro.investigador = form_realizacion.cleaned_data['investigador']
            registro.elenco = form_realizacion.cleaned_data['elenco']
            registro.conductor = form_realizacion.cleaned_data['conductor']
            registro.institucion_productora = form_realizacion.cleaned_data['institucion_productora']
            registro.participantes = form_tecnicas.cleaned_data['idioma_original']
            
            # Guardar el registro en la base de datos
            registro.save()
            
            # Limpiar los datos de la sesión
            del request.session['datos_generales']
            del request.session['descripcion_data']
            del request.session['mapa_data']
            del request.session['realizacion_data']
            
            # Redireccionar a la vista deseada
            return redirect('datosGenerales')
    else:
        form_tecnicas = Tecnicas()
    
    return render(request, 'calificaForm/tecnicas.html', {'formulario': form_tecnicas})





