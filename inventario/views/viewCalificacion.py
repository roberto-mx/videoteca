
# from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from ..forms import Calificacion, Identificacion, Mencion

def crearRegistros(request):
    formulario = Calificacion(request.POST or None)
    return render(request, 'prestañasForm/areaTitulos.html',{'formulario': formulario})

def crearIdentificacion(request):
    formulario = Identificacion(request.POST or None)
    return render(request, 'prestañasForm/areaIdentificación.html',{'formulario': formulario})

def crearMencion(request):
    formulario = Mencion(request.POST or None)
    return render(request, 'prestañasForm/areaMencion.html',{'formulario': formulario})