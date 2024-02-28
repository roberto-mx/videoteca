from django.urls import path

from .views import MaestroCintasListView, MaestroCintasCreateView, MaestroCintasCreateForm, \
    MaestroCintasDetailView, MaestroCintasUpdateView, MaestroCintasDeleteView, MaestroCintasFormView
from .views import DetalleProgramasListView, DetalleProgramasCreateView, \
    DetalleProgramasDetailView, DetalleProgramasUpdateView, DetalleProgramasDeleteView
from .views import FormatosCintasListView, \
    FormatosCintasCreateView, \
    FormatosCintasDetailView, \
    FormatosCintasFormView


app_name = 'inventario'
urlpatterns = [
      
    # Maestro cintas
    path('', MaestroCintasListView.as_view(), name='cintas-list'),
    path('cintas/registrar/', MaestroCintasCreateView.as_view(), name='cintas-create'),
    path('cintas/maestroCintaCreateForm/', MaestroCintasCreateForm, name='maestroCintaCreateForm'),
    path('cintas/<str:pk>/', MaestroCintasDetailView.as_view(), name='cintas-detail'),
    path('cintas/<str:pk>/editar', MaestroCintasUpdateView.as_view(), name='cintas-update'),
    path('cintas/<str:pk>/eliminar', MaestroCintasDeleteView.as_view(), name='cintas-delete'),
    # Detalle programas
    path('programas/', DetalleProgramasListView.as_view(), name='programas-list'),
    path('programas/registrar/', DetalleProgramasCreateView.as_view(), name='programas-create'),
    path('programas/<int:pk>/', DetalleProgramasDetailView.as_view(), name='programas-detail'),
    path('programas/<str:pk>/editar', DetalleProgramasUpdateView.as_view(), name='programas-update'),
    path('programas/<str:pk>/eliminar', DetalleProgramasDeleteView.as_view(), name='programas-delete'),
    
    # CATALOGOS
    # Formatos Cintas
    #path('formatos/formulario/', FormatosCintasFormView.as_view()),
    #path('formatos/', FormatosCintasListView.as_view()),
    #path('formatos/<int:pk>/', FormatosCintasDetailView.as_view()),
    #path('formatos/create/', FormatosCintasCreateView.as_view()),
]