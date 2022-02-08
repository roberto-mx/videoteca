import django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from django.db import connection, transaction, DataError

from datetime import datetime
from enum import Enum

from inventario.models import AltaProd, CalBloques, CalContenido, CalFichatec, CargaMat, CatArea, CatAreac, CatLoc, CatNomsubserv, CatServ, CatStatus, CatTipoprod, ControlVideoteca, DetallePrestamos, DetalleProgramas, FichaContenido, FormatosCintas, HistoriaPrestamos, IngresoMaterial, Invrfid, MaestroCintas, NombreProgramas, OrdenTrabajo, OrigenSerie, OtD, OtM, Personas, PorIngresar, Prestamos, Recupera, RegistroCalificacion, RegistroStock, RegistroSubmaster, RelacionesVideos, SolicitudMaterial, StockMatvirgen, Tbinventario, TipoSerie, Usuarios, UsuariosVid, Videos, VideosPaso, VideosProgramas, VideosRelacionados

import os
import csv
import time
import logging
import json

logger = logging.getLogger(__name__)
to_date = lambda date: datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f') if date != '' else None
to_int = lambda int_value: int(int_value) if int_value.rstrip().isnumeric() else None
to_int_n = lambda int_value: int(int_value) if int_value != '' else None
to_str = lambda str_value: str_value.strip() if str_value else None

def to_date2(date):
    if date == '' or date == 'null':
        return None

    date = date.replace('a. m.', 'AM').replace('p. m.', 'PM').rstrip()
    return datetime.strptime(date, '%d/%m/%Y %I:%M %p')

def to_int2(int_value):
    int_value = int_value.replace(',', '')

    if not int_value.isnumeric():
        return None

    return int(int_value)

 
def get_metadata(file='tables.json'):
    with open(file) as json_file:
        data = json.load(json_file)
    return data.keys()

class Command(BaseCommand):
    help = 'Truncates and load data to tables'
    _flush_value = 100

    def add_arguments(self, parser):
        parser.add_argument('tables', nargs='+', type=str)

    def truncate_table(self, table_name):
        cursor = connection.cursor()
        cursor.execute(f'TRUNCATE TABLE "{table_name.lower()}" CASCADE')
        logger.info(f'[{table_name}] table truncated!')

    def handle(self, *args, **options):

        if len(options['tables']) == 1 and options['tables'][0] == '*':
            logger.info('Load all tables')
            table_list = get_metadata()
        else:
            logger.info(options['tables'])
            table_list = options['tables']

        for table in table_list:
            try:
                self.truncate_table(table)

                path = os.path.join(settings.BASE_DIR, 'CSV', f'{table}.csv')

                with open(path, 'r', encoding="ISO-8859-1") as csv_file:
                    logger.info(f'[{table}] Reading csv...')
                    tic = time.perf_counter()
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    next(csv_reader)
                    if table == 'ALTA_PROD':
                        self.load_alta_prod(csv_reader)
                    elif table == 'CAL_BLOQUES':
                        self.load_cal_bloques(csv_reader)
                    elif table == 'CAL_CONTENIDO':
                        self.load_cal_contenido(csv_reader)
                    elif table == 'CAL_FICHATEC':
                        self.load_cal_ficha_tec(csv_reader)
                    elif table == 'CARGA_MAT':
                        self.load_carga_mat(csv_reader)
                    elif table == 'CAT_AREA':
                        self.load_cat_area(csv_reader)
                    elif table == 'CAT_AREAC':
                        self.load_cat_area_c(csv_reader)
                    elif table == 'CAT_LOC':
                        self.load_cat_loc(csv_reader)
                    elif table == 'CAT_NOMSUBSERV':
                        self.load_cat_nom_subserv(csv_reader)
                    elif table == 'CAT_SERV':
                        self.load_cat_serv(csv_reader)
                    elif table == 'CAT_STATUS':
                        self.load_cat_status(csv_reader)
                    elif table == 'CAT_TIPOPROD':
                        self.load_cat_tipo_prod(csv_reader)
                    elif table == 'CONTROL_VIDEOTECA':
                        self.load_control_videoteca(csv_reader)
                    elif table == 'DETALLE_PRESTAMOS':
                        self.load_detalle_prestamos(csv_reader)
                    elif table == 'DETALLE_PROGRAMAS':
                        self.load_detalle_programas(csv_reader)
                    elif table == 'FICHA_CONTENIDO':
                        self.load_ficha_contenido(csv_reader)
                    elif table == 'FORMATOS_CINTAS':
                        self.load_formatos_cintas(csv_reader)
                    elif table == 'HISTORIA_PRESTAMOS':
                        self.load_historia_prestamos(csv_reader)
                    elif table == 'INGRESO_MATERIAL':
                        self.load_ingreso_material(csv_reader)
                    elif table == 'INVRFID':
                        self.load_inv_rfid(csv_reader)
                    elif table == 'MAESTRO_CINTAS':
                        self.load_maestro_cintas(csv_reader)
                    elif table == 'NOMBRE_PROGRAMAS':
                        self.load_nombre_programas(csv_reader)
                    elif table == 'ORDEN_TRABAJO':
                        self.load_orden_trabajo(csv_reader)
                    elif table == 'ORIGEN_SERIE':
                        self.load_origen_serie(csv_reader)
                    elif table == 'OT_D':
                        self.load_ot_d(csv_reader)
                    elif table == 'OT_M':
                        self.load_ot_m(csv_reader)
                    elif table == 'PERSONAS':
                        self.load_personas(csv_reader)
                    elif table == 'POR_INGRESAR':
                        self.load_por_ingresar(csv_reader)
                    elif table == 'PRESTAMOS':
                        self.load_prestamos(csv_reader)
                    elif table == 'RECUPERA':
                        self.load_recupera(csv_reader)
                    elif table == 'REGISTRO_CALIFICACION':
                        self.load_registro_calificacion(csv_reader)
                    elif table == 'REGISTRO_STOCK':
                        self.load_registro_stock(csv_reader)
                    elif table == 'REGISTRO_SUBMASTER':
                        self.load_registro_submaster(csv_reader)
                    elif table == 'RELACIONES_VIDEOS':
                        self.load_relaciones_videos(csv_reader)
                    elif table == 'SOLICITUD_MATERIAL':
                        self.load_solicitud_material(csv_reader)
                    elif table == 'STOCK_MATVIRGEN':
                        self.load_stock_matvirgen(csv_reader)
                    elif table == 'TBINVENTARIO':
                        self.load_tbinventario(csv_reader)
                    elif table == 'TIPO_SERIE':
                        self.load_tipo_serie(csv_reader)
                    elif table == 'USUARIOS':
                        self.load_usuarios(csv_reader)
                    elif table == 'USUARIOS_VID':
                        self.load_usuarios_vid(csv_reader)
                    elif table == 'VIDEOS':
                        self.load_videos(csv_reader)
                    elif table == 'VIDEOS_PASO':
                        self.load_videos_paso(csv_reader)
                    elif table == 'VIDEOS_PROGRAMAS':
                        self.load_videos_programas(csv_reader)
                    elif table == 'VIDEOS_RELACIONADOS':
                        self.load_videos_relacionados(csv_reader)
                    else:
                        logger.info(f'[{table}] file not found!')
                toc = time.perf_counter()
                logger.info(f'[{table}] data uploaded succesfully! ({toc - tic:0.4f}s elapsed time)')
            except FileNotFoundError:
                raise CommandError(f'[{table}] table does not exist.')

    def load_alta_prod(self, csv_reader):
        for row in csv_reader:
            try:
                AltaProd.objects.create(
                    noproduccion = to_int(row[0]),
                    presup = to_str(row[1]),
                    fecha = to_date(row[2]),
                    id_productor = to_int(row[3]),
                    id_realizador = to_int(row[4]),
                    id_cordinador = to_int(row[5]),
                    prograb = to_str(row[6]),
                    tranvivo = to_str(row[7]),
                    materia = to_str(row[8]),
                    serie = to_str(row[9]),
                    noprogs = to_int(row[10]),
                    mesrealizacion = to_str(row[11]),
                    sinopsis = to_str(row[12]),
                    finicio = to_date(row[13]),
                    fterminacion = to_date(row[14]),
                    observaciones = to_str(row[15]),
                    id_firma_dirvin = to_int(row[16]),
                    id_firma_dirprod = to_int(row[17]),
                    id_firma_recibemat = to_int(row[18]),
                    id_tipoprod = to_int(row[19]),
                    fechap = to_date(row[20]),
                    fgrab = to_str(row[21]),
                    fmontaje = to_str(row[22]),
                    casting = to_int(row[23]),
                    scouting = to_int(row[24]),
                    levimagen = to_int(row[25]),
                    programa = to_int(row[26])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_cal_bloques(self, csv_reader):
        for row in csv_reader:
            try:
                CalBloques.objects.create(
                    vp_id = to_int(row[0]),
                    id_bloque = to_int(row[1]),
                    tc_in = (row[2]),
                    tc_out = to_str(row[3]),
                    duracion = to_str(row[4]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_cal_contenido(self, csv_reader):
        for row in csv_reader:
            try:
                CalContenido.objects.create(
                    vp_id = to_int(row[0]),
                    id_segmento = to_int(row[1]),
                    id_pregunta = to_int(row[2]),
                    respuesta = to_str(row[3]),
                    fecha = to_date(row[4]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_cal_ficha_tec(self, csv_reader):
        for row in csv_reader:
            try:
                CalFichatec.objects.create(
                    vp_id = to_int(row[0]),
                    video = to_int_n(row[1]),
                    set_up = to_int_n(row[2]),
                    chroma = to_int_n(row[3]),
                    drop_out = to_int_n(row[4]),
                    desgarres = to_int_n(row[5]),
                    rayadas = to_int_n(row[6]),
                    hue = to_int_n(row[7]),
                    ch_1 = to_int_n(row[8]),
                    ch_2 = to_int_n(row[9]),
                    falla_ch1 = to_int_n(row[10]),
                    falla_ch2 = to_int_n(row[11]),
                    c_sonido = to_int_n(row[12]),
                    c_audio = to_int(row[13]),
                    tc_in = to_str(row[14]),
                    tc_out = to_str(row[15]),
                    duracion = to_str(row[16]),
                    lip_sync = to_int(row[17]),
                    transmision = to_int(row[18]),
                    motivo_trans = to_str(row[19]),
                    observaciones = to_str(row[20]),
                    califico = to_str(row[21]),
                    fecha = to_date(row[22]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_carga_mat(self, csv_reader):
        for row in csv_reader:
            try:
                CargaMat.objects.create(
                    folio_cb = to_str(row[0]),
                    noproduccion = to_int(row[1]),
                    fprestamo = to_date(row[2]),
                    fdevolucion = to_date(row[3]),
                    codigobarras = to_str(row[4]),
                    form_clave = to_int(row[5]),
                    id_status = to_str(row[6]),
                    id_localizacion = to_int(row[7]),
                    id_solicitud = to_str(row[8]),
                    no_reciclado = to_int(row[9]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_cat_area(self, csv_reader):
        for row in csv_reader:
            try:
                CatArea.objects.create(id_area = to_int(row[0]), area = to_str(row[1]))
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_cat_area_c(self, csv_reader):
        for row in csv_reader:
            try:
                CatAreac.objects.create(id_areac = to_int(row[0]), areac = to_str(row[1]))
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_cat_loc(self, csv_reader):
        for row in csv_reader:
            try:
                CatLoc.objects.create(id_localizacion = to_int(row[0]), localizacion = to_str(row[1]))
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_cat_nom_subserv(self, csv_reader):
        for row in csv_reader:
            try:
                CatNomsubserv.objects.create(
                    id_servicio = to_int(row[0]),
                    id_subserv = to_int(row[1]),
                    nomsubserv = to_str(row[2])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_cat_serv(self, csv_reader):
        for row in csv_reader:
            try:
                CatServ.objects.create(id_servicio = to_int(row[0]), servicio = to_str(row[1]))
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_cat_status(self, csv_reader):
        for row in csv_reader:
            try:
                CatStatus.objects.create(id_status = to_str(row[0]), status = to_str(row[1]), abreviacion = to_str(row[2]))
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_cat_tipo_prod(self, csv_reader):
        for row in csv_reader:
            try:
                CatTipoprod.objects.create(id_tipoprod = to_int(row[0]), tipoprod = to_str(row[1]))
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_control_videoteca(self, csv_reader):
        for row in csv_reader:
            try:
                ControlVideoteca.objects.create(
                        id_control = to_int(row[0]), 
                        fecha = to_date(row[1]), 
                        sistema = to_str(row[2]),
                        movimiento = to_str(row[3]), 
                        tabla = to_str(row[4]),
                        tablakey = to_int(row[5]), 
                        usua_clave = to_str(row[6]),
                        bitacora = to_str(row[7]), 
                        campo = to_str(row[8]), 
                        programa = to_str(row[9])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_detalle_prestamos(self, csv_reader):# refactor
        for row in csv_reader:
            try:
                DetallePrestamos.objects.create(
                    pres_folio = to_int(row[0][:-2]),
                    vide_clave = to_int(row[1][:-2]),
                    depr_estatus = to_str(row[2])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_detalle_programas(self, csv_reader):
        for row in csv_reader:
            try:
                c_barras = to_str(row[2])
                maestro_cintas = MaestroCintas.objects.get(video_cbarras=c_barras)

                DetalleProgramas.objects.create(
                    vp_id=to_int(row[0]),
                    video_id=to_str(row[1]),
                    video_cbarras=maestro_cintas,
                    vp_serie=to_str(row[3]),
                    vp_subtitulo=to_str(row[4]),
                    vp_sinopsis=to_str(row[5]),
                    vp_participantes=to_str(row[6]),
                    vp_personajes=to_str(row[7]),
                    vp_areaconocimiento=to_str(row[8]),
                    vp_asigmateria=to_str(row[9]),
                    vp_niveleducativo=to_str(row[10]),
                    vp_grado=to_str(row[11]),
                    vp_ejetematico=to_str(row[12]),
                    vp_tema=to_str(row[13]),
                    vp_institproductora=to_str(row[14]),
                    vp_idiomaoriginal=to_str(row[15]),
                    vp_elenco=to_str(row[16]),
                    vp_conductor=to_str(row[17]),
                    vp_locutor=to_str(row[18]),
                    vp_guionista=to_str(row[19]),
                    vp_investigador=to_str(row[20]),
                    vp_derechopatrimonial=to_str(row[21]),
                    vp_fechacalificacion=to_date(row[22]),
                    vp_calificador=to_str(row[23]),
                    vp_fecha_modificacion=to_date(row[24]),
                    vp_calificadormod=to_str(row[25]),
                    vp_sistema=to_str(row[26]),
                    vp_duracion=to_str(row[27]),
                    vp_programa=to_str(row[28]),
                    vp_subtitserie=to_str(row[29]),
                    vp_orientacion=to_str(row[30]),
                    vp_duracionin=to_str(row[31]),
                    vp_duracionout=to_str(row[32]),
                    vp_duracion1=to_str(row[33]),
                    tx=to_str(row[34]),
                    vp_observaciones=to_str(row[35]),
                    vp_fork=to_str(row[36]),
                    vp_realizador=to_str(row[37]),
                    vp_musicao=to_str(row[38]),
                    vp_musicai=to_str(row[39]),
                    vp_cantante=to_str(row[40]),
                    vp_disquera=to_str(row[41]),
                    vp_libreriam=to_str(row[42]),
                    vp_registro_obra=to_str(row[43])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_ficha_contenido(self, csv_reader):
        for row in csv_reader:
            try:
                FichaContenido.objects.create(
                    id_segmento = to_int(row[0]),
                    id_pregunta = to_int(row[1]),
                    pregunta = to_str(row[2]),
                    fecha_alta = to_date(row[3]),
                    status = to_str(row[4]),
                    tipo = to_str(row[5]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_formatos_cintas(self, csv_reader):
        for row in csv_reader:
            try:
                FormatosCintas.objects.create(
                    form_clave = to_int(row[0]),
                    form_descripcion = to_str(row[1]),
                    form_duracion = to_str(row[2]),
                    form_prefijo = to_str(row[3])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_formatos_cintas_2(self, csv_reader):
        q_formatos_cintas = '''INSERT INTO FORMATOS_CINTAS 
            (form_clave,form_descripcion,form_duracion,form_prefijo) 
            VALUES(%s,%s,%s,%s)'''
        cont = Command._flush_value
        query_list = []
        cursor = connection.cursor()
        for i, row in enumerate(csv_reader):
            query_list.append( (to_int(row[0]),to_str(row[1]),to_str(row[2]),to_str(row[3])) )
            if i == cont:
                cursor.executemany(q_formatos_cintas, query_list)
                query_list = []
                cont = cont + Command._flush_value
        if len(query_list) > 0:
            cursor.executemany(q_formatos_cintas, query_list)
        transaction.commit()

    def load_historia_prestamos(self, csv_reader):
        for row in csv_reader:
            try:
                HistoriaPrestamos.objects.create(
                    hipr_clave = to_int(row[0][:-2]),
                    usvi_clave = to_int(row[1][:-2]),
                    vide_clave = to_int(row[2][:-2]),
                    hisp_fechahora_registro = to_date(row[3]),
                    hisp_fechahora_devolucion = to_date(row[4]),
                    dev_recibe = to_str(row[5]),
                    dev_folio = to_str(row[6])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_registro_calificacion(self, csv_reader):
        for row in csv_reader:
            try:
                RegistroCalificacion.objects.create(
                    codigo_original = to_str(row[0]),
                    codigo_barras = to_str(row[1]),
                    serie = to_str(row[2]),
                    programa = to_str(row[3]),
                    subtitulo_programa = to_str(row[4]),
                    axo_produccion = to_str(row[5]),
                    duracion = to_str(row[6]),
                    id_productor = to_int(row[7]),
                    productor = to_str(row[8]),
                    id_coordinador = to_int(row[9]),
                    coordinador = to_str(row[10]),
                    sinopsis = to_str(row[11]),
                    participantes = to_str(row[12]),
                    personajes = to_str(row[13]),
                    area_de_conocimiento = to_str(row[14]),
                    asignatura_materia = to_str(row[15]),
                    nivel_educativo = to_str(row[16]),
                    grado = to_str(row[17]),
                    eje_tematico = to_str(row[18]),
                    tema = to_str(row[19]),
                    institucion_productora = to_str(row[20]),
                    derecho_patrimonial = to_str(row[21]),
                    idioma_original = to_str(row[22]),
                    elenco = to_str(row[23]),
                    conductor = to_str(row[24]),
                    locutor = to_str(row[25]),
                    guionista = to_str(row[26]),
                    investigador = to_str(row[27]),
                    fecha_calificacion = to_date(row[28]),
                    calificador = to_str(row[29]),
                    fecha_modificacion = to_date(row[30]),
                    calificador_modificacion = to_str(row[31]),
                    sistema = to_str(row[32]),
                    codigo_orig1 = to_str(row[33]),
                    codigo_submaster1 = to_str(row[34]),
                    codigo_orig2 = to_str(row[35]),
                    codigo_submaster2 = to_str(row[36]),
                    codigo_orig3 = to_str(row[37]),
                    codigo_submaster3 = to_str(row[38]),
                    codigo_orig4 = to_str(row[39]),
                    codigo_submaster4 = to_str(row[40]),
                    codigo_orig5 = to_str(row[41]),
                    codigo_submaster5 = to_str(row[42]),
                    codigo_orig6 = to_str(row[43]),
                    codigo_submaster6 = to_str(row[44]),
                    subtitserie = to_str(row[45]),
                    tiempoin = to_str(row[46]),
                    tiempoout = to_str(row[47]),
                    tiempodur = to_str(row[48]),
                    orientacion = to_str(row[49]),
                    observaciones = to_str(row[50])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_ingreso_material(self, csv_reader):
        for row in csv_reader:
            try:
                IngresoMaterial.objects.create(
                    folio_calificacion = to_str(row[0]),
                    folio_videoteca = to_int(row[1]),
                    fentrega_calificacon = to_str(row[2]),
                    fingreso_videoteca = to_date(row[3]),
                    video_id = to_int(row[4]),
                    numero_produccion = to_int(row[5]),
                    numero_presupuesto = to_int(row[6]),
                    usua_entrega = to_str(row[7]),
                    usua_videoteca = to_str(row[8])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_inv_rfid(self, csv_reader):
        for row in csv_reader:
            try:
                Invrfid.objects.create(video_cbarras = to_str(row[0]))
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_maestro_cintas(self, csv_reader):
        for row in csv_reader:
            try:
                status = to_str(row[5])
                cat_tipo = None if status == '' else CatStatus.objects.get(id_status=status)

                formato_id = to_int(row[2])
                formato = None if formato_id == '' else FormatosCintas.objects.get(form_clave=formato_id)

                tipo_id = to_int(row[22])
                tipo_serie = None if tipo_id == None else TipoSerie.objects.get(tipo_id=tipo_id)

                origen_id = to_int(row[23])
                origen_serie = None if origen_id == None else OrigenSerie.objects.get(origen_id=origen_id)

                MaestroCintas.objects.create(
                        video_id=to_int(row[0]),
                        video_cbarras=to_str(row[1]),
                        form_clave=formato,
                        video_idproduccion=to_int(row[3]),
                        video_codificacion=to_str(row[4]),
                        video_tipo=cat_tipo,
                        video_fingreso=to_date(row[6]),
                        video_inventario=to_str(row[7]),
                        video_estatus=to_str(row[8]),
                        video_rack=to_str(row[9]),
                        video_nivel=to_str(row[10]),
                        video_anoproduccion=to_int(row[11]),
                        video_idproductor=to_int(row[12]),
                        video_productor=to_str(row[13]),
                        video_idcoordinador=to_int(row[14]),
                        video_coordinador=to_str(row[15]),
                        video_usmov=to_int(row[16]),
                        video_fechamov=to_date(row[17]),
                        video_observaciones=to_str(row[18]),
                        usua_clave=to_str(row[19]),
                        video_fchcal=to_date(row[20]),
                        video_target=to_str(row[21]),
                        tipo_id=tipo_serie,
                        origen_id=origen_serie
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break
                

    def load_nombre_programas(self, csv_reader):
        for row in csv_reader:
            try:
                NombreProgramas.objects.create(
                    noproduccion = to_int(row[0]),
                    no_control = to_int(row[1]),
                    nomprog = to_str(row[2]),
                    durprog = to_str(row[3]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_orden_trabajo(self, csv_reader):
        for row in csv_reader:
            try:
                OrdenTrabajo.objects.create(
                    id_ot = to_int(row[0]),
                    sinopsis = to_str(row[1]),
                    tiempo_in = to_str(row[2]),
                    tiempo_out = to_str(row[3]),
                    duracion = to_str(row[4]),
                    id_patrimonial = to_int(row[5]),
                    palabras_clave = to_str(row[6]),
                    areaconocimiento = to_int(row[7]),
                    niveleducativo = to_int(row[8]),
                    asignatura = to_int(row[9]),
                    id_eje = to_int(row[10]),
                    tema = to_str(row[11]),
                    grado = to_int(row[12]),
                    orientacion = to_int(row[13]),
                    observaciones = to_str(row[14]),
                    idioma = to_int(row[15]),
                    sistema = to_int(row[16]),
                    presupuesto = to_str(row[17]),
                    id_instproductora = to_int(row[18]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_origen_serie(self, csv_reader):
        for row in csv_reader:
            try:
                OrigenSerie.objects.create(
                    origen_id = to_int(row[0]),
                    origen = to_str(row[1]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_ot_d(self, csv_reader):
        for row in csv_reader:
            try:
                OtD.objects.create(
                    id_ot = to_int(row[0]),
                    nombre = to_str(row[1]),
                    sinopsis = to_str(row[2]),
                    palabras_c = to_str(row[3]),
                    fecha = to_date(row[4])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_ot_m(self, csv_reader):
        for row in csv_reader:
            try:
                OtM.objects.create(
                    id_ot = to_int(row[0]),
                    asignatura = to_str(row[1]),
                    participantes = to_str(row[2]),
                    nivel_e = to_str(row[3]),
                    presupuesto_b = to_str(row[4]),
                    area_c = to_str(row[5]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_personas(self, csv_reader):
        for row in csv_reader:
            try:
                Personas.objects.create(
                    id_ot = to_int(row[0]),
                    id_personas = to_int(row[1]),
                    id_puesto = to_int(row[2]),
                    nombre = to_str(row[3]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_por_ingresar(self, csv_reader):
        for row in csv_reader:
            try:
                PorIngresar.objects.create(
                    video_cbarras = to_str(row[0]),
                    ingresado = to_str(row[1]),
                    fch_captura = to_date(row[2])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_prestamos(self, csv_reader):
        for row in csv_reader:
            try:
                Prestamos.objects.create(
                    pres_folio = to_int(row[0][:-2]),
                    usvi_clave = to_int(row[1][:-2]),
                    usua_clave = to_str(row[2]),
                    pres_fechahora = to_date(row[3]),
                    pres_fecha_prestamo = to_date(row[4]),
                    pres_fecha_devolucion = to_date(row[5]),
                    pres_estatus = to_str(row[6])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_recupera(self, csv_reader):
        for row in csv_reader:
            try:
                Recupera.objects.create(
                    video_clave = to_str(row[0]),
                    matricula = to_int(row[1]),
                    foliopres = to_int(row[2]),
                    fechapres = to_date(row[3]),
                    fechadev = to_date(row[4]),
                    cbarras = to_str(row[5]),
                    orden = to_int(row[6])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_registro_stock(self, csv_reader):
        for row in csv_reader:
            try:
                RegistroStock.objects.create(
                    codificiacion = to_str(row[0]),
                    codigo_barras = to_str(row[1]),
                    tipo_cinta = to_str(row[2]),
                    consecutivo = to_int(row[3]),
                    serie = to_str(row[4]),
                    subtitserie = to_str(row[5]),
                    programa = to_str(row[6]),
                    subtitulo_programa = to_str(row[7]),
                    axo_produccion = to_str(row[8]),
                    tiempoin = to_str(row[9]),
                    tiempoinf = to_str(row[10]),
                    tiempoout = to_str(row[11]),
                    tiempooutf = to_str(row[12]),
                    tiempodurf = to_str(row[13]),
                    duracion = to_str(row[14]),
                    productor = to_str(row[15]),
                    coordinador = to_str(row[16]),
                    sinopsis = to_str(row[17]),
                    participantes = to_str(row[18]),
                    personajes = to_str(row[19]),
                    institucion_productora = to_str(row[20]),
                    derecho_patrimonial = to_str(row[21]),
                    idioma_original = to_str(row[22]),
                    elenco = to_str(row[23]),
                    conductor = to_str(row[24]),
                    locutor = to_str(row[25]),
                    guionista = to_str(row[26]),
                    investigador = to_str(row[27]),
                    fecha_calificacion = to_date(row[28]),
                    calificador = to_str(row[29]),
                    fecha_modificacion = to_date(row[30]),
                    calificador_modificacion = to_str(row[31]),
                    sistema = to_str(row[32]),
                    observaciones = to_str(row[33]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_registro_submaster(self, csv_reader):
        for row in csv_reader:
            try:
                RegistroSubmaster.objects.create(
                    codigo_original = to_str(row[0]),
                    codigo_barras = to_str(row[1]),
                    serie = to_str(row[2]),
                    programa = to_str(row[3]),
                    subtitulo_programa = to_str(row[4]),
                    axo_produccion = to_int(row[5]),
                    duracion = to_str(row[6].replace('-', '')),
                    id_productor = to_int(row[7]),
                    productor = to_str(row[8]),
                    id_coordinador = to_int(row[9]),
                    coordinador = to_str(row[10]),
                    sinopsis = to_str(row[11]),
                    participantes = to_str(row[12]),
                    personajes = to_str(row[13]),
                    area_de_conocimiento = to_str(row[14]),
                    asignatura_materia = to_str(row[15]),
                    nivel_educativo = to_str(row[16]),
                    grado = to_str(row[17]),
                    eje_tematico = to_str(row[18]),
                    tema = to_str(row[19]),
                    institucion_productora = to_str(row[20]),
                    derecho_patrimonial = to_str(row[21]),
                    idioma_original = to_str(row[22]),
                    elenco = to_str(row[23]),
                    conductor = to_str(row[24]),
                    locutor = to_str(row[25]),
                    guionista = to_str(row[26]),
                    investigador = to_str(row[27]),
                    fecha_calificacion = to_date(row[28]),
                    calificador = to_str(row[29]),
                    fecha_modificacion = to_date(row[30]),
                    calificador_modificacion = to_str(row[31]),
                    sistema = to_str(row[32]),
                    codigo_orig1 = to_str(row[33]),
                    codigo_submaster1 = to_str(row[34]),
                    codigo_orig2 = to_str(row[35]),
                    codigo_submaster2 = to_str(row[36]),
                    codigo_orig3 = to_str(row[37]),
                    codigo_submaster3 = to_str(row[38]),
                    codigo_orig4 = to_str(row[39]),
                    codigo_submaster4 = to_str(row[40]),
                    codigo_orig5 = to_str(row[41]),
                    codigo_submaster5 = to_str(row[42]),
                    codigo_orig6 = to_str(row[43]),
                    codigo_submaster6 = to_str(row[44]),
                    subtitserie = to_str(row[45]),
                    tiempoin = to_str(row[46]),
                    tiempoout = to_str(row[47]),
                    tiempodur = to_str(row[48]),
                    orientacion = to_str(row[49]),
                    observaciones = to_str(row[50]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_relaciones_videos(self, csv_reader):
        for row in csv_reader:
            try:
                RelacionesVideos.objects.create(
                    vide_clave = to_int(row[0][:-2]),
                    revi_clave = to_int(row[1][:-2]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_solicitud_material(self, csv_reader):
        for row in csv_reader:
            try:
                SolicitudMaterial.objects.create(
                    noproduccion = to_int(row[0]),
                    no_control = to_int(row[1]),
                    observacionescintas = to_str(row[2]),
                    cantidad = to_int(row[3]),
                    id_status = to_str(row[4]),
                    form_clave = to_int(row[5]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_stock_matvirgen(self, csv_reader):
        for row in csv_reader:
            try:
                StockMatvirgen.objects.create(
                    folio_cb = to_str(row[0]),
                    codigobarras = to_str(row[1]),
                    id_status = to_str(row[2]),
                    form_clave = to_int(row[3]),
                    no_reciclado = to_int(row[4]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_tbinventario(self, csv_reader):
        for row in csv_reader:
            try:
                Tbinventario.objects.create(cbarras = to_str(row[0]))
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_tipo_serie(self, csv_reader):
        for row in csv_reader:
            try:
                TipoSerie.objects.create(tipo_id = to_int(row[0]), tipo = to_str(row[1]))
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_usuarios(self, csv_reader):
        for row in csv_reader:
            try:
                Usuarios.objects.create(
                    usua_clave = to_str(row[0]),
                    usua_password = to_str(row[1]),
                    usua_nombre = to_str(row[2]),
                    usua_tipo = to_str(row[3]),
                    usua_estatus = to_str(row[4]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_usuarios_vid(self, csv_reader):
        for row in csv_reader:
            try:
                UsuariosVid.objects.create(
                    usvi_clave = to_str(row[0]),
                    usvi_paterno = to_str(row[1]),
                    usvi_materno = to_str(row[2]),
                    usvi_nombre = to_str(row[3]),
                    usvi_maxvideos = to_int(row[4]),
                    usvi_vidpretados = to_int(row[5]),
                    usvi_diasprestamo = to_int(row[6]),
                    usvi_tipo = to_str(row[7]),
                    matricula = to_int(row[8]),
                    area = to_str(row[9]),
                    activo = to_str(row[10]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_videos(self, csv_reader):
        for row in csv_reader:
            try:
                Videos.objects.create(
                    vide_clave = to_int(row[0][:-2]),
                    vide_codigo = to_str(row[1]),
                    vide_videoteca = to_str(row[2]),
                    vide_numero_cinta = to_str(row[3]),
                    vide_tipo_video = to_str(row[4]),
                    form_clave = to_int(row[5]),
                    vide_consecutivo = to_int(row[6]),
                    tivi_clave = to_str(row[7]),
                    usvi_clave = to_int(row[8]),
                    vide_fecha_ingreso = to_str(row[9]),
                    vide_cinta_programa = to_str(row[10]),
                    vide_cintas_totales = to_str(row[11]),
                    vide_programas_totales = to_str(row[12]),
                    vide_inventario = to_str(row[13]),
                    vide_estatus = to_str(row[14]),
                    usua_captura = to_str(row[15]),
                    usua_modifica = to_str(row[16]),
                    vide_fechahora_modificacion = to_date(row[17]),
                    marca = to_str(row[18]),
                    vide_rack = to_str(row[19]),
                    vide_nivel = to_str(row[20]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_videos_paso(self, csv_reader):
        for row in csv_reader:
            try:
                VideosPaso.objects.create(
                    video_id = to_int(row[0]),
                    video_cbarras = to_str(row[1]),
                    video_rel_id = to_int(row[2]),
                    video_rel_cbarras = to_str(row[3]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_videos_programas(self, csv_reader):
        for row in csv_reader:
            try:
                if row[4] == None or row[4] == '':
                    vipr_productor = None
                else:
                    vipr_productor = to_str(row[4][1:-1] if row[4][-1] == '"' else row[4])
                VideosProgramas.objects.create(
                    vide_clave = to_int(row[0][:-2]),
                    vipr_indice = to_int(row[1][:-2]),
                    vipr_serie = to_str(row[2]),
                    vipr_programa = to_str(row[3]),
                    vipr_productor = vipr_productor,
                    vipr_leccion = to_str(row[5]),
                    vipr_ano = to_str(row[6]),
                    vipr_sinopsis = to_str(row[7]),
                    vipr_palabras = to_str(row[8]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break

    def load_videos_relacionados(self, csv_reader):
        for row in csv_reader:
            try:
                VideosRelacionados.objects.create(
                    video_id = to_str(row[0]),
                    video_cbarras = to_str(row[1]),
                    video_rel_id = to_str(row[2]),
                    video_rel_cbarras = to_str(row[3]),
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break
