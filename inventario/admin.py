from django.contrib import admin

from .models import DetalleProgramas
from .models import MaestroCintas


class DetalleProgramasInline(admin.StackedInline):
    model = DetalleProgramas
    extra = 0
    readonly_fields = ('vp_id', 'video_id',)


class MaestroCintasAdmin(admin.ModelAdmin):
    list_display = ['video_id', 'video_cbarras', 'video_tipo', 'video_codificacion', 'video_estatus', 'video_anoproduccion', ]
    list_filter = ['video_tipo', 'video_estatus', ]
    search_fields = ('video_cbarras', )
    inlines = [DetalleProgramasInline]
    fieldsets = [
        (None,               {'fields': ['video_cbarras', 'form_clave', 'video_codificacion', 'video_tipo', 'video_inventario']}),
        ('Datos generales', {'fields': ['video_estatus', 'video_fchcal', 'video_fingreso', 'video_anoproduccion', 'video_productor', 'video_coordinador', 'video_fechamov', 'video_observaciones', 'tipo_id', 'origen_id', 'video_target'], 'classes': ['collapse']}),
    ]
    inlines = [DetalleProgramasInline]
    readonly_fields = ('video_id',)


admin.site.register(MaestroCintas, MaestroCintasAdmin)