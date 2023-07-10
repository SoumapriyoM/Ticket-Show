document.addEventListener("DOMContentLoaded", function() {
  var images = document.querySelectorAll('.background-slideshow .image');
  var index = 0;
  var numImages = images.length;

  function showNextImage() {
    images[index].style.opacity = '0';
    index = (index + 1) % numImages;
    images[index].style.opacity = '1';
    setTimeout(showNextImage, 2000);
  }

  showNextImage();

  setTimeout(function() {
    var alertMsg = document.querySelector('.alert');
    if (alertMsg) {
      alertMsg.remove();
    }
  }, 2000);
});