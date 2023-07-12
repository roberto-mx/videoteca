from django.shortcuts import render, redirect
from django.urls import reverse
from ..forms import Generales, Descripcion, Mapa, Realizacion, Tecnicas
from ..models import RegistroCalificacion

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
            # Obtener los datos del formulario
            datos_generales = request.session.get('datos_generales')
            
            # Actualizar los datos con los campos del formulario actual
            datos_generales.update(formulario.cleaned_data)
            
            # Guardar los datos en la sesión
            request.session['datos_generales'] = datos_generales
            request.session['descripcion_data'] = formulario.cleaned_data
            
            return redirect('mapa')
    else:
        formulario = Descripcion(initial=request.session.get('descripcion_data'))
    return render(request, 'calificaForm/descripcion.html', {'formulario': formulario})

def mapa(request):
    if request.method == 'POST':
        formulario = Mapa(request.POST)
        if formulario.is_valid():
            # Obtener los datos del formulario
            datos_generales = request.session.get('datos_generales')
            descripcion_data = request.session.get('descripcion_data')
            
            # Actualizar los datos con los campos del formulario actual
            datos_generales.update(descripcion_data)
            datos_generales.update(formulario.cleaned_data)
            
            # Guardar los datos en la sesión
            request.session['datos_generales'] = datos_generales
            request.session['descripcion_data'] = descripcion_data
            request.session['mapa_data'] = formulario.cleaned_data
            
            return redirect('realizacion')
    else:
        formulario = Mapa(initial=request.session.get('mapa_data'))
    return render(request, 'calificaForm/mapa.html', {'formulario': formulario})

def realizacion(request):
    if request.method == 'POST':
        formulario = Realizacion(request.POST)
        if formulario.is_valid():
            # Obtener los datos del formulario
            datos_generales = request.session.get('datos_generales')
            descripcion_data = request.session.get('descripcion_data')
            mapa_data = request.session.get('mapa_data')
            
            # Actualizar los datos con los campos del formulario actual
            datos_generales.update(descripcion_data)
            datos_generales.update(mapa_data)
            datos_generales.update(formulario.cleaned_data)
            
            # Guardar los datos en la sesión
            request.session['datos_generales'] = datos_generales
            request.session['descripcion_data'] = descripcion_data
            request.session['mapa_data'] = mapa_data
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
        
        # Actualizar los datos con los campos del formulario actual
        datos_generales.update(tecnicas_data)
        
        # Crear una instancia del formulario de Generales con los datos actualizados
        form_datos_generales = Generales(datos_generales)
        
        # Verificar si el formulario es válido
        if form_datos_generales.is_valid():
            # Guardar los datos en la base de datos
            registro = form_datos_generales.save()
            
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

