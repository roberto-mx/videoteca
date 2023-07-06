


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

from .formsCalif import (
    crearRegistros
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
