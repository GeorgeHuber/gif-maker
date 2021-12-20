//import Webcam from 'webcam-easy';

const webcamElement = document.getElementById('webcam');
const canvasElement = document.getElementById('canvas');
const snapSoundElement = document.getElementById('snapSound');
const webcam = new Webcam(webcamElement, 'user', canvasElement, snapSoundElement);

var loadTimer=null;

function startLoadingScreen(){
    var screen = document.getElementById("loading-screen")
    screen.innerHTML=""
    screen.classList.remove("load-hidden")
    var text = document.createElement("h1")
    screen.appendChild(text)
    var base = "......"
    var dots = 0
    if(loadTimer){
      clearInterval(loadTimer)
    }
    loadTimer = setInterval(()=>{
      text.innerHTML = "Loading"+base.slice(0,dots%4);
      dots++;
    },500)

  
  }

function  stopLoadingScreen(){
    var screen = document.getElementById("loading-screen")
    screen.classList.toggle("load-hidden")
    if (loadTimer){
      clearInterval(loadTimer)
      loadTimer =null;
    }
  }

startLoadingScreen()

webcam.start()
  .then(result =>{
    console.log("webcam started");
  })
  .catch(err => {
    console.log(err);
});

function responseCallback(response){
  console.log(response)
  var canvas = document.getElementById("result")
  canvas.src=response;
  stopLoadingScreen()
  document.getElementById("after-gif").style.display="block"
  document.getElementById("result-text").style.display="block"
  /*
  document.getElementById("result-download").style.display="block"
  document.getElementById("result-download").style.href=response
  document.getElementById("result-hidden").src=response
*/
}

document.getElementById("take-picture").addEventListener("click",()=>{
  console.log(loadTimer)
  if (loadTimer){
    return
  }
  startLoadingScreen()
  let picture = dataURItoBlob(webcam.snap());
  let xhr = new XMLHttpRequest();

  xhr.open("POST", '/makeGif')
  
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4) {
      responseCallback(xhr.response);
    }
  }
  
  let typeSelect = document.getElementById("typeSelect")

  var formData = new FormData();
  formData.append("pictureFile", picture);
  formData.append("gifType", typeSelect.value)
  xhr.send(formData)
})




function dataURItoBlob(dataURI) {
    // convert base64/URLEncoded data component to raw binary data held in a string
    var byteString;
    if (dataURI.split(',')[0].indexOf('base64') >= 0)
        byteString = atob(dataURI.split(',')[1]);
    else
        byteString = unescape(dataURI.split(',')[1]);

    // separate out the mime component
    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

    // write the bytes of the string to a typed array
    var ia = new Uint8Array(byteString.length);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }

    return new Blob([ia], {type:mimeString});
}

stopLoadingScreen()