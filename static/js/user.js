document.addEventListener('DOMContentLoaded', () => {

  document.querySelector('#description_form').style.display = "none";
  document.querySelector('#descrip').onclick = showDescriptionBox;

  // handling user description submission via AJAX
  document.querySelector('#desc_form').onsubmit = () => {
    const request = new XMLHttpRequest();
    const description = document.querySelector('#user_description').value;

    request.open('POST', '/userdescription');

    request.onload = () => {
      const data = JSON.parse(request.responseText);

      if(data.success){
        const new_descrip = data.description
        document.querySelector("#display_user_description").innerHTML = new_descrip;
      }else{
        alert("Description change was unsuccessful");
      }
    };

    const data = new FormData();
    data.append('description', description);

    request.send(data);
    return false;
  };
});

function showDescriptionBox(){
  document.querySelector('#description_form').style.display = "block";
}
