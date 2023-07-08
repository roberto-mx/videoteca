
# from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from ..forms import Calificacion, Identificacion, Mencion, Contenido, Versiones, DescripcionTecnica, AreaDisponibilidad , AreaObservaciones

def areaTitulos(request):
    formulario = Calificacion(request.POST or None)
    return render(request, 'prestañasForm/areaTitulos.html',{'formulario': formulario})

def areaDeIdentificación(request):
    formulario = Identificacion(request.POST or None)
    return render(request, 'prestañasForm/areaIdentificación.html',{'formulario': formulario})

def crearMencion(request):
    formulario = Mencion(request.POST or None)
    return render(request, 'prestañasForm/areaMencion.html',{'formulario': formulario})

def areaContenido(request):
    formulario = Contenido(request.POST or None)
    return render(request, 'prestañasForm/areaContenido.html',{'formulario': formulario})

def areaVersiones(request):
    formulario = Versiones(request.POST or None)
    return render(request, 'prestañasForm/areaVersiones.html',{'formulario': formulario})

def areaDescripcionTecnica(request):
    formulario = DescripcionTecnica(request.POST or None)
    return render(request, 'prestañasForm/areaDescripcionTecnica.html',{'formulario': formulario})

def areaDisponibilidad(request):
    formulario = AreaDisponibilidad(request.POST or None)
    return render(request, 'prestañasForm/areaDisponibilidad.html',{'formulario': formulario})
    
def areaObservaciones(request):
    formulario = AreaObservaciones(request.POST or None)
    return render(request, 'prestañasForm/areaObservaciones.html',{'formulario': formulario})