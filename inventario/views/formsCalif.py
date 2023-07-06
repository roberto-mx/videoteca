
# from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from ..forms import Calificacion

def crearRegistros(request):
    formulario = Calificacion(request.POST or None)

    return render(request, 'prestamos/crearRegistros.html',{'formulario': formulario})