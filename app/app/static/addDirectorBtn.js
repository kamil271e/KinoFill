//var value = $("#.director-field").attr("height");
var value = document.getElementById("director-field").attr("top");

document.write(value);
$("#director-btn").css("top", value);