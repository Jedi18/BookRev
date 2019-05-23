document.addEventListener('DOMContentLoaded', () => {

  var typingTimer;
  var timerInterval = 2500;

  document.querySelector("#bookid").addEventListener('keyup', () => {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(getBookInfo,timerInterval);
  });

  function getBookInfo(){
    const request = new XMLHttpRequest();
    const book_id  = document.querySelector("#bookid").value;

    request.open('GET', `/apiid/${book_id}`);

    request.onload = () => {
      const data = JSON.parse(request.responseText);
      if(data.success){
        document.querySelector("#bookinfo").innerHTML = `${data.title} - ${data.author} , Year - ${data.year}<br>ISBN - ${data.isbn} <br>`;
      }else{
      }
    };

    request.send();

  }

});

function updateRatingSlider(val)
{
  document.getElementById('ratingsValue').value = val;
}
