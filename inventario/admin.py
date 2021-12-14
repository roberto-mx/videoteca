from django.contrib import admin

from .models import FormatosCintas
from .models import DetalleProgramas
from .models import MaestroCintas


class DetalleProgramasInline(admin.StackedInline):
    model = DetalleProgramas
    extra = 1


class MaestroCintasAdmin(admin.ModelAdmin):
    list_display = ['video_id', 'video_cbarras', 'video_tipo', 'video_codificacion', 'video_estatus', 'video_anoproduccion', ]
    list_filter = ['video_tipo', 'video_estatus', ]
    search_fields = ('video_cbarras', )
    #inlines = [DetalleProgramasInline]
    #fieldsets = [
    #    (None,               {'fields': ['question_text']}),
    #    ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    #]
    #inlines = [DetalleProgramasInline]


admin.site.register(MaestroCintas, MaestroCintasAdmin)
#admin.site.register(FormatosCintas)
