function showErrorPopup(message) {
    var popup = document.createElement("div");
    popup.style.position = "fixed";
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    popup.style.backgroundColor = "white";
    popup.style.padding = "20px";
    popup.style.boxShadow = "0 0 10px black";
    popup.innerHTML = message + '<br><br><button onclick="closePopup()">Aceptar</button>';
    document.body.appendChild(popup);
  }
  
  function closePopup() {
    var popup = document.querySelector("div");
    popup.remove();
  }