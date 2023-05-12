const alertMessage = (type, message, title) => {
  Swal.fire
  ({
    icon:   type,
    title:  title,
    text:   message,
  });
}

const alertMessageContent = (title, text, icon, showCancelButton, confirmButtonColor, cancelButtonColor) => {
  Swal.fire({
    title: title,
    text: text,
    icon: icon,
    showCancelButton: showCancelButton,
    confirmButtonColor: confirmButtonColor,
    cancelButtonColor: cancelButtonColor,
    confirmButtonText: 'Si, continuar!'
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire(
        'Exportado!',
        'Su archivo a sido exportado.',
        'success'
      )
    }
  });
};