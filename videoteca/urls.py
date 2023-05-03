"""videoteca URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from inventario.views import login, PrestamosListView, PrestamoDetalle,Filtrar_prestamos,ejemplo, Filtrar_pres_Folio, generar_pdf, generar_pdf_modal, GetFolioPrestamo, GetFolioDetail, RegisterInVideoteca, ValidateOutVideoteca, RegisterOutVideoteca, EndInVideoteca
from django.contrib.auth import views
from django.views.generic import TemplateView

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path('admin/', admin.site.urls),
    path('inventario/', include('inventario.urls'), name="inventario_list"),
    path('prestamos/', PrestamosListView.as_view(), name='prestamos_list' ),
    path('prestamos/detalles/', PrestamoDetalle, name='prestamos_detalles' ),
    path('prestamos/detalles/filter', Filtrar_prestamos, name='prestamos_filter' ),
    path('prestamos/detalles/filter/folio', Filtrar_pres_Folio, name='prestamos_filter_folio' ),
    path('prestamos/generate_pdf', generar_pdf, name='generar_pdf'),
    path('prestamos/ejemplo', ejemplo, name='ejemplo'),
    path('prestamos/generate_pdf_modal', generar_pdf_modal, name='generar_pdf_modal'),
    path('search_folio/<int:pk>', GetFolioPrestamo, name='search_folio_prestamo'),
    path('detail_folio/<int:pk>', GetFolioDetail, name='search_folio_detail'),
    path('register_in/', RegisterInVideoteca,  name="registro_entrada_videoteca"),
    path('validate_out/', ValidateOutVideoteca,  name="validacion_salida_videoteca"),
    path('register_out/', RegisterOutVideoteca,  name="registro_salida_videoteca"),
    path('end_in/', EndInVideoteca,  name="finalizar_entrada_videoteca"),


    
    
]
