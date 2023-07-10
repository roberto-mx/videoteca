
# from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from ..forms import Calificacion, Identificacion, Mencion, Contenido, Versiones, DescripcionTecnica, AreaDisponibilidad, AreaObservaciones  

def areaTitulos(request):
    formulario = Calificacion(request.POST or None)
    return render(request, 'calificaForm/areaTitulos.html',{'formulario': formulario})

def areaDeIdentificación(request):
    formulario = Identificacion(request.POST or None)
    return render(request, 'calificaForm/areaDeIdentificación.html',{'formulario': formulario})

def areaMencion(request):
    formulario = Mencion(request.POST or None)
    return render(request, 'calificaForm/areaMencion.html',{'formulario': formulario})

def areaContenido(request):
    formulario = Contenido(request.POST or None)
    return render(request, 'calificaForm/areaContenido.html',{'formulario': formulario})

def areaVersiones(request):
    formulario = Versiones(request.POST or None)
    return render(request, 'calificaForm/areaVersiones.html',{'formulario': formulario})

def areaDescripcionTecnica(request):
    formulario = DescripcionTecnica(request.POST or None)
    return render(request, 'calificaForm/areaDescripcionTecnica.html',{'formulario': formulario})

def areaDisponibilidad(request):
    formulario = AreaDisponibilidad(request.POST or None)
    return render(request, 'calificaForm/areaDisponibilidad.html',{'formulario': formulario})
    
# def areaObservaciones(request):
#     formulario = AreaObservaciones(request.POST or None)
#     return render(request, 'calificaForm/areaObservaciones.html',{'formulario': formulario})

def areaObservaciones(request):
    formulario = AreaObservaciones(request.POST or None)
    if request.method == 'POST':
        if formulario.is_valid():
            # Obtener los datos de las vistas anteriores
            datos_titulos = request.session.get('datos_titulos')
            datos_identificacion = request.session.get('datos_identificacion')
            datos_mencion = request.session.get('datos_mencion')
            datos_contenido = request.session.get('datos_contenido')
            datos_versiones = request.session.get('datos_versiones')
            datos_descripcion_tecnica = request.session.get('datos_descripcion_tecnica')
            # Obtener los datos de la vista actual
            datos_observaciones = formulario.cleaned_data
            # Combinar todos los datos en uno solo
            datos_totales = {
                **datos_titulos,
                **datos_identificacion,
                **datos_mencion,
                **datos_contenido,
                **datos_versiones,
                **datos_descripcion_tecnica,
                **datos_observaciones
            }
            # Guardar los datos en la base de datos
            formulario = Calificacion(datos_totales)
            formulario.save()
            return redirect('prestamos_list')  # Redirige a la página de éxito o a otra vista
    else:
        # Guardar los datos de la vista actual en la sesión
        if formulario.is_bound:
            request.session['datos_observaciones'] = formulario.cleaned_data
    return render(request, 'calificaForm/areaObservaciones.html', {'formulario': formulario})
