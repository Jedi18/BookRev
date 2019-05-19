document.addEventListener('DOMContentLoaded', () => {

  document.querySelector('#description_form').style.display = "none";
  document.querySelector('#descrip').onclick = showDescriptionBox;
});

function showDescriptionBox(){
  document.querySelector('#description_form').style.display = "block";
}
