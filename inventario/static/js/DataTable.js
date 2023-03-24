const generarDataTable = () => {
  
  const defaultOptions = {
    "paging": true,
    "searching": true,
    "autoWidth": false,
    "ordering": true,
    "lengthMenu": [
      [5, 25, 50, 100, 150, 200, 500, 1000, -1],
      [5, 25, 50, 100, 150, 200, 500, "Todo"]
    ],
    "order": [[1, "asc"]],
    "scrollX": true,
    "scrollCollapse": true,
    "bDestroy": true,
    "ordering": false,
    "language": {
      "sProcessing": "Procesando...",
      "sLengthMenu": "Mostrar _MENU_ registros",
      "sZeroRecords": "No se encontraron resultados",
      "sEmptyTable": "Ningun dato disponible en esta tabla",
      "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
      "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
      "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
      "sInfoPostFix": "",
      "sSearch": "Buscar:",
      "sUrl": "",
      "sInfoThousands": ",",
      "sLoadingRecords": "Cargando...",
      "oPaginate": {
        "pagingType": "numbers",
        "sFirst": "Primero",
        "sLast": "Último",
        "sNext": "Siguiente",
        "sPrevious": "Anterior",
        "pagingType": "numbers"
      },
      "oAria": {
        "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
        "sSortDescending": ": Activar para ordenar la columna de manera descendente"
      }
    }
  };
  
  return defaultOptions
}
