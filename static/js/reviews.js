document.addEventListener('DOMContentLoaded', () => {

  var typingTimer;
  var timerInterval = 2500;

  setTimeout(getBookInfo, 1000);

  document.querySelector("#bookid").addEventListener('keyup', () => {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(getBookInfo,timerInterval);
  });

  function getBookInfo(){
    const book_id  = document.querySelector("#bookid").value;
    const request = new XMLHttpRequest();

    if(book_id == "")
    {
      return;
    }

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
