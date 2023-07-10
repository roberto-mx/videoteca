


from .maestrocintas import (
    login,
    DetalleProgramasDeleteView,
    DetalleProgramasUpdateView,
    DetalleProgramasCreateView,
    MaestroCintasCreateForm,
    DetalleProgramasDetailView,
    DetalleProgramasCreateView,
    DetalleProgramasUpdateView,
    DetalleProgramasDetailView,
    DetalleProgramasCreateView,
    DetalleProgramasListView,
    MaestroCintasFormView,
    MaestroCintasDeleteView, 
    MaestroCintasUpdateView, 
    MaestroCintasDetailView, 
    MaestroCintasCreateView, 
    MaestroCintasListView, 
    FormatosCintasCreateView, 
    FormatosCintasDetailView, 
    FormatosCintasListView, 
    FormatosCintasFormView
    
)

from .viewCalificacion import (
    areaTitulos,
    areaDeIdentificación,
    areaMencion,
    areaContenido,
    areaVersiones,
    areaDescripcionTecnica,
    areaDisponibilidad,
    areaObservaciones
)


from .prestamos import (
    PrestamosListView,
    DetallesListView,
    obtenerPeoplePerson,
    GetFolioPrestamo,
    GetFolioDetail,
    RegisterInVideoteca,
    ValidateOutVideoteca,
    RegisterOutVideoteca,
    PrestamoDetalle,
    Filtrar_prestamos,
    EndInVideoteca,
    
    
)
from .reports import generar_pdf, generar_pdf_modal, generate_pdf_resgister_folio, GetFilePdf
