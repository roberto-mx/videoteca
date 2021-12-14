from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from django.db import connection, transaction, DataError

from datetime import datetime
from enum import Enum

from inventario.models import AltaProd, CalBloques, CalContenido, CalFichatec, CargaMat, CatArea, CatAreac, CatLoc, CatNomsubserv, CatServ, CatStatus, CatTipoprod, ControlVideoteca, DetallePrestamos, DetalleProgramas, FichaContenido, HistoriaPrestamos, IngresoMaterial, Invrfid, MaestroCintas, NombreProgramas, OrdenTrabajo, OrigenSerie, OtD, OtM, Personas, PorIngresar, Prestamos, Recupera, RegistroCalificacion, RegistroStock, RegistroSubmaster, RelacionesVideos, SolicitudMaterial, StockMatvirgen, Tbinventario, TipoSerie, Usuarios, UsuariosVid, Videos, VideosPaso, VideosProgramas, VideosRelacionados

import os
import csv
import time
import logging

to_date = lambda date: datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f') if date != '' else None
to_int = lambda int_value: int(int_value) if int_value.isnumeric() else None
logger = logging.getLogger(__name__)


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


table_names = ['ALTA_PROD', 'CAL_BLOQUES', 'CAL_CONTENIDO', 'CAL_FICHATEC', 'CARGA_MAT', 'CAT_AREA', 
        'CAT_AREAC', 'CAT_LOC', 'CAT_NOMSUBSERV', 'CAT_SERV', 'CAT_STATUS', 'CAT_TIPOPROD', 'CONTROL_VIDEOTECA', 
        'DETALLE_PRESTAMOS', 'DETALLE_PROGRAMAS', 'FICHA_CONTENIDO', 'FORMATOS_CINTAS', 'HISTORIA_PRESTAMOS', 
        'INGRESO_MATERIAL', 'INVRFID', 'MAESTRO_CINTAS', 'NOMBRE_PROGRAMAS', 'ORDEN_TRABAJO', 'ORIGEN_SERIE', 
        'OT_D', 'OT_M', 'PERSONAS', 'POR_INGRESAR', 'PRESTAMOS', 'RECUPERA', 'REGISTRO_CALIFICACION', 
        'REGISTRO_STOCK', 'REGISTRO_SUBMASTER', 'RELACIONES_VIDEOS', 'SOLICITUD_MATERIAL', 'STOCK_MATVIRGEN', 
        'TBINVENTARIO', 'TIPO_SERIE', 'USUARIOS', 'USUARIOS_VID', 'VIDEOS', 'VIDEOS_PASO', 'VIDEOS_PROGRAMAS', 
        'VIDEOS_RELACIONADOS', 
]
q_control_videoteca = '''INSERT INTO control_videoteca 
        (id_control, fecha, sistema, movimiento, tabla, tablakey, usua_clave, bitacora, campo, programa)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
q_historia_prestamos = '''INSERT INTO historia_prestamos 
        (hipr_clave, usvi_clave, vide_clave, hisp_fechahora_registro, hisp_fechahora_devolucion, dev_recibe, dev_folio) 
        VALUES(%s,%s,%s,%s,%s,%s,%s)'''
q_formatos_cintas = '''INSERT INTO FORMATOS_CINTAS 
        (form_clave,form_descripcion,form_duracion,form_prefijo) 
        VALUES(%s,%s,%s,%s)'''
q_detalle_programas = '''INSERT INTO DETALLE_PROGRAMAS
        (vp_id,video_id,video_cbarras,vp_serie,vp_subtitulo,vp_sinopsis,
        vp_participantes,vp_personajes, vp_areaconocimiento,vp_asigmateria,
        vp_niveleducativo,vp_grado,vp_ejetematico,vp_tema,vp_institproductora,
        vp_idiomaoriginal,vp_elenco,vp_conductor,vp_locutor,vp_guionista,
        vp_investigador,vp_derechopatrimonial,vp_fechacalificacion,vp_calificador,
        vp_fecha_modificacion,vp_calificadormod,vp_sistema,vp_duracion,vp_programa,
        vp_subtitserie,vp_orientacion,vp_duracionin,vp_duracionout,vp_duracion1,
        tx,vp_observaciones,vp_fork,vp_realizador,vp_musicao,vp_musicai,
        vp_cantante,vp_disquera,vp_libreriam,vp_registro_obra) VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
         %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''


class Command(BaseCommand):
    help = f'Truncates and load data to tables\nExecute:\n\tpython manage.py loaddata t_name=<TABLE_NAME>\nTables:\n\t{table_names}'
    flush_value = 100

    def add_arguments(self, parser):
        parser.add_argument('t_name', nargs='+', type=str)

        """parser.add_argument(
            '--truncate',
            action='truncate_table',
            help='Truncate table instead of load data',
        )"""

    def truncate_table(self, table_name):
        cursor = connection.cursor()
        cursor.execute(f'TRUNCATE TABLE "{table_name.lower()}" CASCADE')
        logger.info(f'[{table_name}] table truncated!')

    def handle(self, *args, **options):
        path = 'D:\\aprende\\Robert\\'

        print(options['t_name'][1:])
        #if options['truncate']:
        #    self.truncate_table()

        for table in options['t_name'][1:]:
            try:
                self.truncate_table(table)

                with open(os.path.join(path, f'{table}.csv'), 'r', encoding="ISO-8859-1") as csv_file:
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
                        logger.info(f'[{table}] not found!')
                toc = time.perf_counter()
                logger.info(f'[{table}] data uploaded succesfully! ({toc - tic:0.4f}s elapsed time)')
            except FileNotFoundError:
                raise CommandError(f'[{table}] table does not exist.')

    def load_alta_prod(self, csv_reader):
        for row in csv_reader:
            AltaProd.objects.create(
                noproduccion = to_int(row[0]),
                presup = row[1],
                fecha = to_date(row[2]),
                id_productor = to_int(row[3]),
                id_realizador = to_int(row[4]),
                id_cordinador = to_int(row[5]),
                prograb = row[6],
                tranvivo = row[7],
                materia = row[8],
                serie = row[9],
                noprogs = to_int(row[10]),
                mesrealizacion = row[11],
                sinopsis = row[12],
                finicio = to_date(row[13]),
                fterminacion = to_date(row[14]),
                observaciones = row[15],
                id_firma_dirvin = to_int(row[16]),
                id_firma_dirprod = to_int(row[17]),
                id_firma_recibemat = to_int(row[18]),
                id_tipoprod = to_int(row[19]),
                fechap = to_date(row[20]),
                fgrab = row[21],
                fmontaje = row[22],
                casting = to_int(row[23]),
                scouting = to_int(row[24]),
                levimagen = to_int(row[25]),
                programa = to_int(row[26])
            )

    def load_cal_bloques(self, csv_reader):
        for row in csv_reader:
            CalBloques.objects.create(
                vp_id = to_int(row[0]),
                id_bloque = to_int(row[1]),
                tc_in = row[2],
                tc_out = row[3],
                duracion = row[4],
            )

    def load_cal_contenido(self, csv_reader):
        for row in csv_reader:
            CalContenido.objects.create(
                vp_id = to_int(row[0]),
                id_segmento = to_int(row[1]),
                id_pregunta = to_int(row[2]),
                respuesta = row[3],
                fecha = to_date(row[4]),
            )

    def load_cal_ficha_tec(self, csv_reader):
        for row in csv_reader:
            CalFichatec.objects.create(
                vp_id = to_int(row[0]),
                video = to_int(row[1]),
                set_up = to_int(row[2]),
                chroma = to_int(row[3]),
                drop_out = to_int(row[4]),
                desgarres = to_int(row[5]),
                rayadas = to_int(row[6]),
                hue = to_int(row[7]),
                ch_1 = to_int(row[8]),
                ch_2 = to_int(row[9]),
                falla_ch1 = to_int(row[10]),
                falla_ch2 = to_int(row[11]),
                c_sonido = to_int(row[12]),
                c_audio = to_int(row[13]),
                tc_in = row[14],
                tc_out = row[15],
                duracion = row[16],
                lip_sync = to_int(row[17]),
                transmision = to_int(row[18]),
                motivo_trans = row[19],
                observaciones = row[20],
                califico = row[21],
                fecha = to_date(row[22]),
            )

    def load_carga_mat(self, csv_reader):
        for row in csv_reader:
            CargaMat.objects.create(
                folio_cb = row[0],
                noproduccion = to_int(row[1]),
                fprestamo = to_date(row[2]),
                fdevolucion = to_date(row[3]),
                codigobarras = row[4],
                form_clave = to_int(row[5]),
                id_status = row[6],
                id_localizacion = to_int(row[7]),
                id_solicitud = row[8],
                no_reciclado = to_int(row[9]),
            )

    def load_cat_area(self, csv_reader):
        for row in csv_reader:
            CatArea.objects.create(id_area = to_int(row[0]), area = row[1])

    def load_cat_area_c(self, csv_reader):
        for row in csv_reader:
            CatAreac.objects.create(id_areac = to_int(row[0]), areac = row[1])

    def load_cat_loc(self, csv_reader):
        for row in csv_reader:
            CatLoc.objects.create(id_localizacion = to_int(row[0]), localizacion = row[1])

    def load_cat_nom_subserv(self, csv_reader):
        for row in csv_reader:
            CatNomsubserv.objects.create(
                id_servicio = to_int(row[0]),
                id_subserv = to_int(row[1]),
                nomsubserv = row[2]
            )

    def load_cat_serv(self, csv_reader):
        for row in csv_reader:
            CatServ.objects.create(id_servicio = to_int(row[0]), servicio = row[1])

    def load_cat_status(self, csv_reader):
        for row in csv_reader:
            CatStatus.objects.create(id_status = row[0], status = row[1], abreviacion = row[2])

    def load_cat_tipo_prod(self, csv_reader):
        for row in csv_reader:
            CatTipoprod.objects.create(id_tipoprod = to_int(row[0]), tipoprod = row[1])

    def load_control_videoteca(self, csv_reader):
        """for row in csv_reader:
            ControlVideoteca.objects.create(
                    id_control = to_int(row[0]), 
                    fecha = to_date(row[1]), 
                    sistema = row[2],
                    movimiento = row[3], 
                    tabla = row[4],
                    tablakey = to_int(row[5]), 
                    usua_clave = row[6],
                    bitacora = row[7], 
                    campo = row[8], 
                    programa = row[9]
            )"""
        cont = Command.flush_value
        query_list = []
        
        cursor = connection.cursor()
        for i, row in enumerate(csv_reader):
            if len(row) != 10:
                print(row)
                continue
            query_list.append(
                (
                    to_int(row[0]), to_date(row[1]), row[2], row[3], 
                    row[4], to_int(row[5]), row[6], row[7], row[8], row[9]
                )
            )
            if i == cont:
                cursor.executemany(q_control_videoteca, query_list)
                query_list = []
                cont = cont + Command.flush_value
        if len(query_list) > 0:
            cursor.executemany(q_control_videoteca, query_list)
        transaction.commit()

    def load_detalle_prestamos(self, csv_reader):# refactor
        for row in csv_reader:
            DetallePrestamos.objects.create(
                pres_folio = to_int(row[0]),
                vide_clave = to_int(row[1]),
                depr_estatus = row[2]
            )

    def load_detalle_programas(self, csv_reader):
        cont = Command.flush_value
        query_list = []
        
        cursor = connection.cursor()
        for i, row in enumerate(csv_reader):
            query_list.append(
                (
                    to_int(row[0]),row[1],row[2],row[3],row[4],row[5],row[6],
                    row[7],row[8],row[9],row[10],row[11],row[12],row[13],
                    row[14],row[15],row[16],row[17],row[18],row[19],row[20],
                    row[21],to_date(row[22]),row[23],to_date(row[24]),row[25],
                    row[26],row[27],row[28],row[29],row[30],row[31],row[32],
                    row[33],row[34],row[35],row[36],row[37],row[38],row[39],
                    row[40],row[41],row[42],row[43],
                )
            )
            if i == cont:
                cursor.executemany(q_detalle_programas, query_list)
                query_list = []
                cont = cont + Command.flush_value
        if len(query_list) > 0:
            cursor.executemany(q_detalle_programas, query_list)
        transaction.commit()

    def load_ficha_contenido(self, csv_reader):
        for row in csv_reader:
            FichaContenido.objects.create(
                id_segmento = to_int(row[0]),
                id_pregunta = to_int(row[1]),
                pregunta = row[2],
                fecha_alta = to_date(row[3]),
                status = row[4],
                tipo = row[5],
            )

    def load_formatos_cintas(self, csv_reader):
        cont = Command.flush_value
        query_list = []

        cursor = connection.cursor()
        for i, row in enumerate(csv_reader):
            query_list.append( (to_int(row[0]),row[1],row[2],row[3]) )
            if i == cont:
                cursor.executemany(q_formatos_cintas, query_list)
                query_list = []
                cont = cont + Command.flush_value
        if len(query_list) > 0:
            cursor.executemany(q_formatos_cintas, query_list)
        transaction.commit()

    def load_historia_prestamos(self, csv_reader):
        """for row in csv_reader:
            HistoriaPrestamos.objects.create(hipr_clave = to_int(row[0]), usvi_clave = to_int(row[1]),vide_clave = to_int(row[2]),
            hisp_fechahora_registro = to_date(row[3]),hisp_fechahora_devolucion = to_date(row[4]),dev_recibe = row[5],dev_folio = row[6])"""
        cont = Command.flush_value
        query_list = []
        
        cursor = connection.cursor()
        for i, row in enumerate(csv_reader):
            query_list.append(
                (
                    to_int(row[0]), to_int(row[1]), to_int(row[2]), 
                    to_date(row[3]), to_date(row[4]), row[5], row[6]
                )
            )
            if i == cont:
                cursor.executemany(q_historia_prestamos, query_list)
                query_list = []
                cont = cont + Command.flush_value
        if len(query_list) > 0:
            cursor.executemany(q_historia_prestamos, query_list)
        transaction.commit()

    def load_registro_calificacion(self, csv_reader):
        for row in csv_reader:
            RegistroCalificacion.objects.create(
                codigo_original = row[0],
                codigo_barras = row[1],
                serie = row[2],
                programa = row[3],
                subtitulo_programa = row[4],
                axo_produccion = row[5],
                duracion = row[6],
                id_productor = to_int(row[7]),
                productor = row[8],
                id_coordinador = to_int(row[9]),
                coordinador = row[10],
                sinopsis = row[11],
                participantes = row[12],
                personajes = row[13],
                area_de_conocimiento = row[14],
                asignatura_materia = row[15],
                nivel_educativo = row[16],
                grado = row[17],
                eje_tematico = row[18],
                tema = row[19],
                institucion_productora = row[20],
                derecho_patrimonial = row[21],
                idioma_original = row[22],
                elenco = row[23],
                conductor = row[24],
                locutor = row[25],
                guionista = row[26],
                investigador = row[27],
                fecha_calificacion = to_date(row[28]),
                calificador = row[29],
                fecha_modificacion = to_date(row[30]),
                calificador_modificacion = row[31],
                sistema = row[32],
                codigo_orig1 = row[33],
                codigo_submaster1 = row[34],
                codigo_orig2 = row[35],
                codigo_submaster2 = row[36],
                codigo_orig3 = row[37],
                codigo_submaster3 = row[38],
                codigo_orig4 = row[39],
                codigo_submaster4 = row[40],
                codigo_orig5 = row[41],
                codigo_submaster5 = row[42],
                codigo_orig6 = row[43],
                codigo_submaster6 = row[44],
                subtitserie = row[45],
                tiempoin = row[46],
                tiempoout = row[47],
                tiempodur = row[48],
                orientacion = row[49],
                observaciones = row[50]
            )

    def load_ingreso_material(self, csv_reader):
        for row in csv_reader:
            IngresoMaterial.objects.create(
                folio_calificacion = row[0],
                folio_videoteca = to_int(row[1]),
                fentrega_calificacon = row[2],
                fingreso_videoteca = to_date(row[3]),
                video_id = to_int(row[4]),
                numero_produccion = to_int(row[5]),
                numero_presupuesto = to_int(row[6]),
                usua_entrega = row[7],
                usua_videoteca = row[8]
            )

    def load_inv_rfid(self, csv_reader):
        for row in csv_reader:
            Invrfid.objects.create(video_cbarras = row[0])

    def load_maestro_cintas(self, csv_reader):
        for row in csv_reader:
            try:
                MaestroCintas.objects.create(
                        video_id=to_int(row[0]),
                        video_cbarras=row[1],
                        form_clave=row[2],
                        video_idproduccion=to_int(row[3]),
                        video_codificacion=row[4].rstrip(),
                        video_tipo=row[5],
                        video_fingreso=to_date(row[6]),
                        video_inventario=row[7],
                        video_estatus=row[8].rstrip(),
                        video_rack=row[9],
                        video_nivel=row[10],
                        video_anoproduccion=to_int(row[11]),
                        video_idproductor=to_int(row[12]),
                        video_productor=row[13].rstrip(),
                        video_idcoordinador=to_int(row[14]),
                        video_coordinador=row[15].rstrip(),
                        video_usmov=to_int(row[16]),
                        video_fechamov=to_date(row[17]),
                        video_observaciones=row[18],
                        usua_clave=row[19],
                        video_fchcal=to_date(row[20]),
                        video_target=row[21],
                        id_tipo=to_int(row[22]),
                        id_origen=to_int(row[23])
                )
            except DataError as ex:
                logger.error(row)
                logger.error(ex)
                break
                

    def load_nombre_programas(self, csv_reader):
        for row in csv_reader:
            NombreProgramas.objects.create(
                noproduccion = to_int(row[0]),
                no_control = to_int(row[1]),
                nomprog = row[2],
                durprog = row[3],
            )

    def load_orden_trabajo(self, csv_reader):
        for row in csv_reader:
            OrdenTrabajo.objects.create(
                id_ot = to_int(row[0]),
                sinopsis = row[1],
                tiempo_in = row[2],
                tiempo_out = row[3],
                duracion = row[4],
                id_patrimonial = to_int(row[5]),
                palabras_clave = row[6],
                areaconocimiento = to_int(row[7]),
                niveleducativo = to_int(row[8]),
                asignatura = to_int(row[9]),
                id_eje = to_int(row[10]),
                tema = row[11],
                grado = to_int(row[12]),
                orientacion = to_int(row[13]),
                observaciones = row[14],
                idioma = to_int(row[15]),
                sistema = to_int(row[16]),
                presupuesto = row[17],
                id_instproductora = to_int(row[18]),
            )

    def load_origen_serie(self, csv_reader):
        for row in csv_reader:
            OrigenSerie.objects.create(
                id_origen = to_int(row[0]),
                origen = row[1],
            )

    def load_ot_d(self, csv_reader):
        for row in csv_reader:
            OtD.objects.create(
                id_ot = to_int(row[0]),
                nombre = row[1],
                sinopsis = row[2],
                palabras_c = row[3],
                fecha = to_date(row[4])
            )

    def load_ot_m(self, csv_reader):
        for row in csv_reader:
            OtM.objects.create(
                id_ot = to_int(row[0]),
                asignatura = row[1],
                participantes = row[2],
                nivel_e = row[3],
                presupuesto_b = row[4],
                area_c = row[5],
            )

    def load_personas(self, csv_reader):
        for row in csv_reader:
            Personas.objects.create(
                id_ot = to_int(row[0]),
                id_personas = to_int(row[1]),
                id_puesto = to_int(row[2]),
                nombre = row[3],
            )

    def load_por_ingresar(self, csv_reader):
        for row in csv_reader:
            PorIngresar.objects.create(
                video_cbarras = row[0],
                ingresado = row[1],
                fch_captura = to_date(row[2])
            )

    def load_prestamos(self, csv_reader):
        for row in csv_reader:
            Prestamos.objects.create(
                pres_folio = to_int(row[0]),
                usvi_clave = to_int(row[1]),
                usua_clave = row[2],
                pres_fechahora = to_date(row[3]),
                pres_fecha_prestamo = to_date(row[4]),
                pres_fecha_devolucion = to_date(row[5]),
                pres_estatus = row[6]
            )

    def load_recupera(self, csv_reader):
        for row in csv_reader:
            Recupera.objects.create(
                video_clave = row[0],
                matricula = to_int(row[1]),
                foliopres = to_int(row[2]),
                fechapres = to_date(row[3]),
                fechadev = to_date(row[4]),
                cbarras = row[5],
                orden = to_int(row[6])
            )

    def load_registro_stock(self, csv_reader):
        for row in csv_reader:
            RegistroStock.objects.create(
                codificiacion = row[0],
                codigo_barras = row[1],
                tipo_cinta = row[2],
                consecutivo = to_int(row[3]),
                serie = row[4],
                subtitserie = row[5],
                programa = row[6],
                subtitulo_programa = row[7],
                axo_produccion = row[8],
                tiempoin = row[9],
                tiempoinf = row[10],
                tiempoout = row[11],
                tiempooutf = row[12],
                tiempodurf = row[13],
                duracion = row[14],
                productor = row[15],
                coordinador = row[16],
                sinopsis = row[17],
                participantes = row[18],
                personajes = row[19],
                institucion_productora = row[20],
                derecho_patrimonial = row[21],
                idioma_original = row[22],
                elenco = row[23],
                conductor = row[24],
                locutor = row[25],
                guionista = row[26],
                investigador = row[27],
                fecha_calificacion = to_date(row[28]),
                calificador = row[29],
                fecha_modificacion = to_date(row[30]),
                calificador_modificacion = row[31],
                sistema = row[32],
                observaciones = row[33],
            )

    def load_registro_submaster(self, csv_reader):
        for row in csv_reader:
            RegistroSubmaster.objects.create(
                codigo_original = row[0],
                codigo_barras = row[1],
                serie = row[2],
                programa = row[3],
                subtitulo_programa = row[4],
                axo_produccion = to_int(row[5]),
                duracion = row[6],
                id_productor = to_int(row[7]),
                productor = row[8],
                id_coordinador = to_int(row[9]),
                coordinador = row[10],
                sinopsis = row[11],
                participantes = row[12],
                personajes = row[13],
                area_de_conocimiento = row[14],
                asignatura_materia = row[15],
                nivel_educativo = row[16],
                grado = row[17],
                eje_tematico = row[18],
                tema = row[19],
                institucion_productora = row[20],
                derecho_patrimonial = row[21],
                idioma_original = row[22],
                elenco = row[23],
                conductor = row[24],
                locutor = row[25],
                guionista = row[26],
                investigador = row[27],
                fecha_calificacion = to_date(row[28]),
                calificador = row[29],
                fecha_modificacion = to_date(row[30]),
                calificador_modificacion = row[31],
                sistema = row[32],
                codigo_orig1 = row[33],
                codigo_submaster1 = row[34],
                codigo_orig2 = row[35],
                codigo_submaster2 = row[36],
                codigo_orig3 = row[37],
                codigo_submaster3 = row[38],
                codigo_orig4 = row[39],
                codigo_submaster4 = row[40],
                codigo_orig5 = row[41],
                codigo_submaster5 = row[42],
                codigo_orig6 = row[43],
                codigo_submaster6 = row[44],
                subtitserie = row[45],
                tiempoin = row[46],
                tiempoout = row[47],
                tiempodur = row[48],
                orientacion = row[49],
                observaciones = row[50],
            )

    def load_relaciones_videos(self, csv_reader):
        for row in csv_reader:
            RelacionesVideos.objects.create(
                vide_clave = to_int(row[0]),
                revi_clave = to_int(row[1]),
            )

    def load_solicitud_material(self, csv_reader):
        for row in csv_reader:
            SolicitudMaterial.objects.create(
                noproduccion = to_int(row[0]),
                no_control = to_int(row[1]),
                observacionescintas = row[2],
                cantidad = to_int(row[3]),
                id_status = row[4],
                form_clave = to_int(row[5]),
            )

    def load_stock_matvirgen(self, csv_reader):
        for row in csv_reader:
            StockMatvirgen.objects.create(
                folio_cb = row[0],
                codigobarras = row[1],
                id_status = row[2],
                form_clave = to_int(row[3]),
                no_reciclado = to_int(row[4]),
            )

    def load_tbinventario(self, csv_reader):
        for row in csv_reader:
            Tbinventario.objects.create(cbarras = row[0])

    def load_tipo_serie(self, csv_reader):
        for row in csv_reader:
            TipoSerie.objects.create(id_tipo = to_int(row[0]), tipo = row[1])

    def load_usuarios(self, csv_reader):
        for row in csv_reader:
            Usuarios.objects.create(
                usua_clave = row[0],
                usua_password = row[1],
                usua_nombre = row[2],
                usua_tipo = row[3],
                usua_estatus = row[4],
            )

    def load_usuarios_vid(self, csv_reader):
        for row in csv_reader:
            UsuariosVid.objects.create(
                usvi_clave = row[0],
                usvi_paterno = row[1],
                usvi_materno = row[2],
                usvi_nombre = row[3],
                usvi_maxvideos = to_int(row[4]),
                usvi_vidpretados = to_int(row[5]),
                usvi_diasprestamo = to_int(row[6]),
                usvi_tipo = row[7],
                matricula = to_int(row[8]),
                area = row[9],
                activo = row[10],
            )

    def load_videos(self, csv_reader):
        for row in csv_reader:
            Videos.objects.create(
                vide_clave = to_int(row[0]),
                vide_codigo = row[1],
                vide_videoteca = row[2],
                vide_numero_cinta = row[3],
                vide_tipo_video = row[4],
                form_clave = to_int(row[5]),
                vide_consecutivo = to_int(row[6]),
                tivi_clave = row[7],
                usvi_clave = to_int(row[8]),
                vide_fecha_ingreso = row[9],
                vide_cinta_programa = row[10],
                vide_cintas_totales = row[11],
                vide_programas_totales = row[12],
                vide_inventario = row[13],
                vide_estatus = row[14],
                usua_captura = row[15],
                usua_modifica = row[16],
                vide_fechahora_modificacion = to_date(row[17]),
                marca = row[18],
                vide_rack = row[19],
                vide_nivel = row[20],
            )

    def load_videos_paso(self, csv_reader):
        for row in csv_reader:
            VideosPaso.objects.create(
                video_id = to_int(row[0]),
                video_cbarras = row[1],
                video_rel_id = to_int(row[2]),
                video_rel_cbarras = row[3],
            )

    def load_videos_programas(self, csv_reader):
        for row in csv_reader:
            if len(row[6]) > 45:
                print(row[6])
            VideosProgramas.objects.create(
                vide_clave = to_int(row[0]),
                vipr_indice = to_int(row[1]),
                vipr_serie = row[2].rstrip(),
                vipr_programa = row[3].rstrip(),
                vipr_productor = row[4].rstrip(),
                vipr_leccion = row[5].rstrip(),
                vipr_ano = row[6].rstrip("\b\t "),
                vipr_sinopsis = row[7].rstrip(),
                vipr_palabras = row[8].rstrip(),
            )

    def load_videos_relacionados(self, csv_reader):
        for row in csv_reader:
            VideosRelacionados.objects.create(
                video_id = row[0],
                video_cbarras = row[1],
                video_rel_id = row[2],
                video_rel_cbarras = row[3],
            )
