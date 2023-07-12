from django.shortcuts import render
from ..forms import Generales, Descripcion, Mapa, Realizacion, Tecnicas
from ..models import RegistroCalificacion


def datosGenerales(request):
    formulario = Generales(request.POST or None)
    return render(request, 'calificaForm/datosGenerales.html', {'formulario': formulario})


def descripcion(request):
    formulario = Descripcion(request.POST or None)
    return render(request, 'calificaForm/descripcion.html', {'formulario': formulario})


def mapa(request):
    formulario = Mapa(request.POST or None)
    return render(request, 'calificaForm/mapa.html', {'formulario': formulario})


def realizacion(request):
    formulario = Realizacion(request.POST or None)
    return render(request, 'calificaForm/realizacion.html', {'formulario': formulario})


def tecnicas(request):
    formulario = Tecnicas(request.POST or None)
    if request.method == 'POST':
        if formulario.is_valid():
            # Acceder a los datos de las secciones anteriores
            datos_generales = formulario.cleaned_data
            descripcion = formulario.cleaned_data.get('sinopsis')
            mapa = formulario.cleaned_data.get('area_de_conocimiento')
            realizacion = formulario.cleaned_data.get('guionista')

            # Realizar el guardado en la base de datos utilizando el modelo RegistroCalificacion
            registro = RegistroCalificacion()
            registro.codigo_barras = datos_generales['codigo_barras']
            registro.fecha_calificacion = datos_generales['fecha_calificacion']
            registro.axo_produccion = datos_generales['axo_produccion']
            registro.productor = datos_generales['productor']
            registro.coordinador = datos_generales['coordinador']
            registro.observaciones = datos_generales['observaciones']
            registro.serie = datos_generales['serie']
            registro.duracion = datos_generales['duracion']
            registro.subtitserie = datos_generales['subtitserie']
            registro.programa = datos_generales['programa']
            registro.subtitulo_programa = datos_generales['subtitulo_programa']
            registro.sinopsis = descripcion
            registro.area_de_conocimiento = mapa
            registro.guionista = realizacion

            # Guardar el registro en la base de datos
            registro.save()

            # Redireccionar o realizar alguna otra acción después del guardado

    return render(request, 'calificaForm/tecnicas.html', {'formulario': formulario})
