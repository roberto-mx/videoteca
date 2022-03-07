from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

import datetime
import re

from .forms import Login, MaestrosCintasForm
from .forms import MaestroCintasFilter, FormatosCintasForm

from .models import CatStatus
from .models import DetalleProgramas
from .models import FormatosCintas
from .models import MaestroCintas
from .models import OrigenSerie


class AdminLogin(LoginView):
    template_name = 'login.html'



class FormatosCintasFormView(FormView):
    #template_name = 'formatoscintas_form.html'
    form_class = FormatosCintasForm
    success_url = '/'
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super().form_valid(form)


class FormatosCintasListView(ListView):
    model = FormatosCintas
    #queryset = FormatosCintas.objects.all()
    context_object_name = 'formatos_list'
    #template_name = 'formatos_list.html'
    paginate_by = 3
    def get_queryset(self):
        """Return FormatosCintas."""
        return FormatosCintas.objects.all()[:7]
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cat_status'] = CatStatus.objects.all()
        return context


class FormatosCintasDetailView(DetailView):
    model = FormatosCintas
    #queryset = FormatosCintas.objects.all()
    #def get_object(self):
    #    obj = super().get_object()
    #    # Record the last accessed date
    #    obj.save()
    #    return obj


class FormatosCintasCreateView(CreateView):
    model = FormatosCintas
    fields = ['form_clave', 'form_descripcion', 'form_duracion', 'form_prefijo']


# -------------------
# Maestro cintas
# -------------------

#@method_decorator(login_required, name='dispatch')
class MaestroCintasListView(ListView):
    model = MaestroCintas
    context_object_name = 'mcintas_list'
    ordering = ['-video_cbarras']
    paginate_by = 10
    page_range = 4
    no_search_result = False
    cbarras = ''
    formato = '-'
    tipo = ''
    status = ''
    anio = ''
    estatus = {
        '1': 'En Videoteca',
        '2': 'En Calificacion',
        '3': 'Cinta Extraviada',
        '4': 'Baja por Daño'
    }

    #def get_queryset(self, **kwargs):
    #    search_results = MaestroCintasFilter(self.request.GET, self.queryset)
    #    self.no_search_result = True if not search_results.qs else False
    #    # Returns the default queryset if an empty queryset is returned by the django_filters
    #    # You could as well return just the search result's queryset if you want to
    #    return search_results.qs.distinct() or self.model.objects.all()

    def get_query_string(self):
        query_string = self.request.META.get("QUERY_STRING", "")
        # Get all queries excluding pages from the request's meta
        validated_query_string = "&".join([x for x in re.findall(
            r"(\w*=\w{1,})", query_string) if not "page=" in x])
        # Avoid passing the query path to template if no search result is found using the previous query
        return "&" + validated_query_string if (validated_query_string and self.no_search_result) else ""

    def get_queryset(self):
        self.cbarras = self.request.GET.get('q', '')
        self.formato = self.request.GET.get('formato', '')
        self.tipo = self.request.GET.get('tipo', '')
        self.status = self.request.GET.get('status', '')
        self.anio = self.request.GET.get('anio', '')
        self.no_search_result = self.cbarras != '' or self.formato != '' \
            or self.tipo != '' or self.status != '' or self.anio != ''
        rs = MaestroCintas.objects.all().order_by('video_cbarras')
        if self.cbarras != '':
            rs = rs.filter(video_cbarras__contains=self.cbarras)
        if self.formato != '':
            rs = rs.filter(form_clave=self.formato)
        if self.tipo != '':
            rs = rs.filter(video_tipo=self.tipo)
        if self.status != '':
            rs = rs.filter(video_estatus=self.estatus[self.status])
        if self.anio != '':
            rs = rs.filter(video_fechamov__year=int(self.anio))
        return rs

    #def get_ordering(self):
    #    ordering = self.request.GET.get('ordering', '-video_fechamov')
    #    # validate ordering here
    #    return ordering
    
    def get_context_data(self, **kwargs):
        context = super(MaestroCintasListView, self).get_context_data(**kwargs)
        context['tipo_list'] = CatStatus.objects.all()
        context['formatos_list'] = FormatosCintas.objects.all()

        context["no_search_result"] = self.no_search_result
        context["query_string"] = self.get_query_string()
        context['cbarras_filter'] = self.cbarras
        context['formato_filter'] = int(self.formato) if self.formato != '' else 0
        context['tipo_filter'] = self.tipo
        context['status_filter'] = self.status
        context['anio_filter'] = self.anio

        cintas = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(cintas, self.paginate_by)
        try:
            cintas = paginator.page(page)
        except PageNotAnInteger:
            cintas = paginator.page(1)
        except EmptyPage:
            cintas = paginator.page(paginator.num_pages)
        context['mcintas_list'] = cintas

        return context


class MaestroCintasCreateView(CreateView):
    model = MaestroCintas
    template_name = 'inventario/maestrocintas_create.html'
    #fields = ('video_id', 'video_cbarras', 'form_clave', 'video_codificacion', 
    #    'video_codificacion', 'video_tipo', 'video_fingreso', 'video_inventario',
    #    'video_estatus', 'video_rack', 'video_nivel', 'video_anoproduccion',
    #    'video_idproductor', 'video_productor', 'video_idcoordinador', 
    #    'video_coordinador', 'video_usmov', 'video_fechamov', 'video_observaciones',
    #    'usua_clave', 'video_fchcal', 'video_target', 'tipo_id', 'origen_id')
    form_class = MaestrosCintasForm
    success_url = reverse_lazy('inventario:cintas-list')


#@method_decorator(login_required, name='dispatch')
class MaestroCintasDetailView(DetailView):
    model = MaestroCintas
    template_name = 'inventario/maestrocintas_detail.html'
    context_object_name = 'cinta'
    def get_context_data(self, **kwargs):
        context = super(MaestroCintasDetailView, self).get_context_data(**kwargs)
        context['programas'] = DetalleProgramas.objects.filter(video_cbarras=self.object.video_cbarras)
        return context


#@method_decorator(login_required, name='dispatch')
class MaestroCintasUpdateView(UpdateView):
    model = MaestroCintas
    template_name = 'inventario/maestrocintas_update.html'
    context_object_name = 'cinta'
    form_class = MaestrosCintasForm
    #fields = ('video_id', 'video_cbarras', 'form_clave', 'video_codificacion', 
    #    'video_codificacion', 'video_tipo', 'video_fingreso', 'video_inventario',
    #    'video_estatus', 'video_rack', 'video_nivel', 'video_anoproduccion',
    #    'video_idproductor', 'video_productor', 'video_idcoordinador', 
    #    'video_coordinador', 'video_usmov', 'video_fechamov', 'video_observaciones',
    #    'usua_clave', 'video_fchcal', 'video_target', 'tipo_id', 'origen_id',)

    def form_valid(self, form):
        form.instance.video_fechamov = datetime.datetime.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('inventario:cintas-detail', kwargs={'pk': self.object.video_cbarras})


#@method_decorator(login_required, name='dispatch')
class MaestroCintasDeleteView(DeleteView):
    model = MaestroCintas
    template_name = 'inventario/maestrocintas_delete.html'
    success_url = reverse_lazy('inventario:cintas-list')


class MaestroCintasFormView(FormView):
    template_name = 'maestrocintas_form.html'
    form_class = MaestrosCintasForm
    success_url = '/'


# -------------------
# Detalle programas
# -------------------


class DetalleProgramasListView(ListView):
    model = DetalleProgramas
    context_object_name = 'programas_list'
    paginate_by = 10
    #def get_context_data(self, **kwargs):
    #    context = super(DetalleProgramasListView, self).get_context_data(**kwargs)
    #    return context


class DetalleProgramasCreateView(CreateView):
    model = DetalleProgramas
    template_name = 'inventario/detalleprogramas_create.html'
    fields = ('vp_id', 'video_id', 'vp_serie', 'vp_subtitulo',#, 'video_cbarras'
        'vp_sinopsis', 'vp_participantes', 'vp_personajes', 'vp_areaconocimiento',
        'vp_asigmateria', 'vp_niveleducativo', 'vp_grado', 'vp_ejetematico',
        'vp_tema', 'vp_institproductora', 'vp_idiomaoriginal', 'vp_elenco',
        'vp_conductor', 'vp_locutor', 'vp_guionista', 'vp_investigador',
        'vp_derechopatrimonial', 'vp_fechacalificacion', 'vp_calificador',
        'vp_fecha_modificacion', 'vp_calificadormod', 'vp_sistema', 'vp_duracion',
        'vp_programa', 'vp_subtitserie', 'vp_orientacion', 'vp_duracionin',
        'vp_duracionout', 'vp_duracion1', 'tx', 'vp_observaciones', 'vp_fork',
        'vp_realizador', 'vp_musicao', 'vp_musicai', 'vp_cantante', 'vp_disquera',
        'vp_libreriam', 'vp_registro_obra')
    success_url = reverse_lazy('inventario:cintas-list')



#@method_decorator(login_required, name='dispatch')
class DetalleProgramasDetailView(DetailView):
    model = DetalleProgramas
    template_name = 'inventario/detalleprogramas_detail.html'
    context_object_name = 'programa'


#@method_decorator(login_required, name='dispatch')
class DetalleProgramasUpdateView(UpdateView):
    model = DetalleProgramas
    template_name = 'inventario/detalleprogramas_update.html'
    context_object_name = 'programa'
    fields = ('vp_id', 'video_id', 'vp_serie', 'vp_subtitulo',#, 'video_cbarras'
        'vp_sinopsis', 'vp_participantes', 'vp_personajes', 'vp_areaconocimiento',
        'vp_asigmateria', 'vp_niveleducativo', 'vp_grado', 'vp_ejetematico',
        'vp_tema', 'vp_institproductora', 'vp_idiomaoriginal', 'vp_elenco',
        'vp_conductor', 'vp_locutor', 'vp_guionista', 'vp_investigador',
        'vp_derechopatrimonial', 'vp_fechacalificacion', 'vp_calificador',
        'vp_fecha_modificacion', 'vp_calificadormod', 'vp_sistema', 'vp_duracion',
        'vp_programa', 'vp_subtitserie', 'vp_orientacion', 'vp_duracionin',
        'vp_duracionout', 'vp_duracion1', 'tx', 'vp_observaciones', 'vp_fork',
        'vp_realizador', 'vp_musicao', 'vp_musicai', 'vp_cantante', 'vp_disquera',
        'vp_libreriam', 'vp_registro_obra')

    def get_success_url(self):
        return reverse_lazy('inventario:programas-detail', kwargs={'pk': self.object.vp_id})


#@method_decorator(login_required, name='dispatch')
class DetalleProgramasDeleteView(DeleteView):
    model = DetalleProgramas
    template_name = 'inventario/detalleprogramas_delete.html'
    success_url = reverse_lazy('inventario:inventario-list')


# -------------------
# Detalle programas
# -------------------


def login(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = Login(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')
    else:
        form = Login()

    return render(request, 'login.html', {'form': form})