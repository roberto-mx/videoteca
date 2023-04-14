const alertMessage = (type, message, title) => {
  Swal.fire
  ({
    icon:   type,
    title:  title,
    text:   message,
  });
}

