const alertMessage = (type, message, title, button) => {
  Swal.fire({
    icon: type,
    title: title,
    text: message,
    confirmButtonColor: button
  });
};

const messageAlerta = (type, message, title, button) => {
  Swal.fire({
    //position: 'top-center',
    icon: type,
    title: title,
    text: message,
    showConfirmButton: true,
    timer: false,
    confirmButtonColor: button
  });
};

const alertMessageContent = (type, message, title, confirmButtonColor, cancelButtonColor) => {
  Swal.fire({
    icon: type,
    text: message,
    title: title,
    confirmButtonColor: confirmButtonColor,
    cancelButtonColor: cancelButtonColor,
    showCancelButton: true, // Mostrar el botón de cancelar
    confirmButtonText: 'Si, continuar!',
    cancelButtonText: 'Cancelar', // Texto del botón de cancelar
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({
        icon: 'success',
        title: '¡Muy bien!',
        text: 'Se inserto una nueva cinta.',
      })
    }
  });
};

