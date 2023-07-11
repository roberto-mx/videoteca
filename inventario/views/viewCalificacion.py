# from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from ..forms import Generales, Descripcion, Mapa, Realizacion, Tecnicas
from tempus_dominus.widgets import DateTimePicker


def datosGenerales(request):
    formulario = Generales(request.POST or None)
    return render(request, 'calificaForm/datosGenerales.html',{'formulario': formulario})

def descripcion(request):
    formulario = Descripcion(request.POST or None)
    return render(request, 'calificaForm/descripcion.html',{'formulario': formulario})

def mapa(request):
    formulario = Mapa(request.POST or None)
    return render(request, 'calificaForm/mapa.html',{'formulario': formulario})

def realizacion(request):
    formulario = Realizacion(request.POST or None)
    return render(request, 'calificaForm/realizacion.html',{'formulario': formulario})

def tecnicas(request):
    formulario = Tecnicas(request.POST or None)
    return render(request, 'calificaForm/tecnicas.html',{'formulario': formulario})

