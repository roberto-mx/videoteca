from django.db import models

class MaestroCintas(models.Model):
    video_id = models.IntegerField(verbose_name="Id")
    video_cbarras = models.CharField(max_length=12, verbose_name="Código de barras")
    form_clave = models.IntegerField(verbose_name="Clave")
    video_idproduccion = models.IntegerField(blank=True, null=True, verbose_name="Id producción")
    video_codificacion = models.CharField(max_length=20, blank=True, null=True, verbose_name="Codificación")
    video_tipo = models.CharField(max_length=1, blank=True, null=True, verbose_name="Tipo")
    video_fingreso = models.DateTimeField(blank=True, null=True, verbose_name="Fecha ingreso")
    video_inventario = models.CharField(max_length=4, blank=True, null=True, verbose_name="Inventario")
    video_estatus = models.CharField(max_length=20, verbose_name="Estatus de la cinta")
    video_rack = models.CharField(max_length=4, blank=True, null=True, verbose_name="Rack")
    video_nivel = models.CharField(max_length=4, blank=True, null=True, verbose_name="Nivel")
    video_anoproduccion = models.IntegerField(blank=True, null=True, verbose_name="Año de producción")
    video_idproductor = models.IntegerField(blank=True, null=True, verbose_name="Id de productor")
    video_productor = models.CharField(max_length=55, blank=True, null=True, verbose_name="Productor")
    video_idcoordinador = models.IntegerField(blank=True, null=True, verbose_name="Id de coordinador")
    video_coordinador = models.CharField(max_length=60, blank=True, null=True, verbose_name="Coordinador")
    video_usmov = models.IntegerField(blank=True, null=True, verbose_name="usmov")
    video_fechamov = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de movimiento")
    video_observaciones = models.CharField(max_length=238, blank=True, null=True, verbose_name="Observaciones")
    usua_clave = models.CharField(max_length=10, blank=True, null=True, verbose_name="Clave")
    video_fchcal = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de calificación")
    video_target = models.CharField(max_length=20, blank=True, null=True, verbose_name="Target")
    id_tipo = models.IntegerField(blank=True, null=True, verbose_name="Tipo de cinta")
    id_origen = models.IntegerField(blank=True, null=True, verbose_name="Origen")

    class Meta:
        db_table = 'maestro_cintas'
        verbose_name = 'Material videograbado'
        verbose_name_plural = 'Material videograbado'


class DetalleProgramas(models.Model):
    vp_id = models.IntegerField(primary_key=True, verbose_name="Id")
    video_id = models.IntegerField(verbose_name="Video Id")
    video_cbarras = models.CharField(max_length=12, verbose_name="Código de barras")
    vp_serie = models.CharField(max_length=300, blank=True, null=True, verbose_name="Serie")
    vp_subtitulo = models.CharField(max_length=150, blank=True, null=True, verbose_name="Subtítulo")
    vp_sinopsis = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Sinopsis")
    vp_participantes = models.CharField(max_length=250, blank=True, null=True, verbose_name="Participantes")
    vp_personajes = models.CharField(max_length=250, blank=True, null=True, verbose_name="Personajes")
    vp_areaconocimiento = models.CharField(max_length=50, blank=True, null=True, verbose_name="Area de conocimiento")
    vp_asigmateria = models.CharField(max_length=50, blank=True, null=True, verbose_name="Asig materia")
    vp_niveleducativo = models.CharField(max_length=38, blank=True, null=True, verbose_name="Nivel educativo")
    vp_grado = models.CharField(max_length=40, blank=True, null=True, verbose_name="Grado")
    vp_ejetematico = models.CharField(max_length=100, blank=True, null=True, verbose_name="Eje temático")
    vp_tema = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tema")
    vp_institproductora = models.CharField(max_length=300, blank=True, null=True, verbose_name="Institución productora")
    vp_idiomaoriginal = models.CharField(max_length=40, blank=True, null=True, verbose_name="Idioma original")
    vp_elenco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Elenco")
    vp_conductor = models.CharField(max_length=60, blank=True, null=True, verbose_name="Conductor")
    vp_locutor = models.CharField(max_length=60, blank=True, null=True, verbose_name="Locutor")
    vp_guionista = models.CharField(max_length=60, blank=True, null=True, verbose_name="Guionista")
    vp_investigador = models.CharField(max_length=60, blank=True, null=True, verbose_name="Investigador")
    vp_derechopatrimonial = models.CharField(max_length=60, blank=True, null=True, verbose_name="Fecha de Calificación")
    vp_fechacalificacion = models.DateTimeField(blank=True, null=True, verbose_name="Derecho patrimonial")
    vp_calificador = models.CharField(max_length=5, blank=True, null=True, verbose_name="Calificador")
    vp_fecha_modificacion = models.DateTimeField(blank=True, null=True, verbose_name="Última Actualización")
    vp_calificadormod = models.CharField(max_length=5, blank=True, null=True, verbose_name="Calificador mod")
    vp_sistema = models.CharField(max_length=4, blank=True, null=True, verbose_name="Sistema")
    vp_duracion = models.CharField(max_length=10, blank=True, null=True, verbose_name="Duración")
    vp_programa = models.CharField(max_length=300, blank=True, null=True, verbose_name="Programa")
    vp_subtitserie = models.TextField(blank=True, null=True, verbose_name="Subtitulos de serie")
    vp_orientacion = models.CharField(max_length=160, blank=True, null=True, verbose_name="Orientación")
    # Tiempos
    vp_duracionin = models.CharField(max_length=165, blank=True, null=True, verbose_name="In")
    vp_duracionout = models.CharField(max_length=165, blank=True, null=True, verbose_name="Out")
    vp_duracion1 = models.CharField(max_length=165, blank=True, null=True, verbose_name="Duración")

    tx = models.CharField(max_length=160, blank=True, null=True, verbose_name="TX")
    vp_observaciones = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Observaciones")
    vp_fork = models.CharField(max_length=300, blank=True, null=True, verbose_name="Fork")
    vp_realizador = models.CharField(max_length=600, blank=True, null=True, verbose_name="Realizador")
    vp_musicao = models.CharField(max_length=600, blank=True, null=True, verbose_name="Música de cierre")
    vp_musicai = models.CharField(max_length=600, blank=True, null=True, verbose_name="Música de apertura")
    vp_cantante = models.CharField(max_length=600, blank=True, null=True, verbose_name="Cantante")
    vp_disquera = models.CharField(max_length=600, blank=True, null=True, verbose_name="Disquera")
    vp_libreriam = models.CharField(max_length=600, blank=True, null=True, verbose_name="Libreria m")
    vp_registro_obra = models.CharField(max_length=600, blank=True, null=True, verbose_name="Registro de Obra")

    class Meta:
        db_table = 'detalle_programas'
