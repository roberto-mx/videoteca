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

from .forms import Login, MaestrosCintasForm
from .forms import FormatosCintasForm

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

@method_decorator(login_required, name='dispatch')
class MaestroCintasListView(ListView):
    #template_name = 'formatoscintas_form.html'
    model = MaestroCintas
    context_object_name = 'mcintas_list'
    ordering = ['-video_cbarras']
    paginate_by = 10
    page_range = 4

    #def get_queryset(self):
    #    cbarras = self.request.GET.get('q')
    #    formato = self.request.GET.get('formato', '0')
    #    anio = self.request.GET.get('anio', '0')
    #    rs = MaestroCintas.objects.all().order_by('video_cbarras')
    #    if cbarras:
    #        rs = rs.filter(video_cbarras__contains=cbarras)
    #    if formato:
    #        rs = rs.filter(form_clave=formato)
    #    return rs

    #def get_ordering(self):
    #    ordering = self.request.GET.get('ordering', '-date_created')
    #    # validate ordering here
    #    return ordering
    
    def get_context_data(self, **kwargs):
        context = super(MaestroCintasListView, self).get_context_data(**kwargs)
        context['status_list'] = CatStatus.objects.all()
        context['formatos_list'] = FormatosCintas.objects.all()
        context['origen_list'] = OrigenSerie.objects.all()

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
    fields = ('video_id', 'video_cbarras', 'form_clave', 'video_codificacion', 
        'video_codificacion', 'video_tipo', 'video_fingreso', 'video_inventario',
        'video_estatus', 'video_rack', 'video_nivel', 'video_anoproduccion',
        'video_idproductor', 'video_productor', 'video_idcoordinador', 
        'video_coordinador', 'video_usmov', 'video_fechamov', 'video_observaciones',
        'usua_clave', 'video_fchcal', 'video_target', 'tipo_id', 'origen_id')
    success_url = '/inventario'#reverse_lazy('inventario:cintas-list')


@method_decorator(login_required, name='dispatch')
class MaestroCintasDetailView(DetailView):
    model = MaestroCintas
    template_name = 'inventario/maestrocintas_detail.html'
    context_object_name = 'cinta'
    def get_context_data(self, **kwargs):
        context = super(MaestroCintasDetailView, self).get_context_data(**kwargs)
        context['programas'] = DetalleProgramas.objects.filter(video_cbarras=self.object.video_cbarras)
        return context


@method_decorator(login_required, name='dispatch')
class MaestroCintasUpdateView(UpdateView):
    model = MaestroCintas
    template_name = 'inventario/maestrocintas_update.html'
    context_object_name = 'cinta'
    fields = ('video_cbarras', 'form_clave', 'video_codificacion',)

    def get_success_url(self):
        return reverse_lazy('inventario:cinta-detail', kwargs={'pk': self.object.id})


@method_decorator(login_required, name='dispatch')
class MaestroCintasDeleteView(DeleteView):
    model = MaestroCintas
    template_name = 'inventario/maestrocintas_delete.html'
    success_url = '/inventario'#reverse_lazy('inventario:inventario-list')


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



@method_decorator(login_required, name='dispatch')
class DetalleProgramasDetailView(DetailView):
    model = DetalleProgramas
    template_name = 'inventario/detalleprogramas_detail.html'
    context_object_name = 'programa'


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

    # if a GET (or any other method) we'll create a blank form
    else:
        form = Login()

    return render(request, 'name.html', {'form': form})