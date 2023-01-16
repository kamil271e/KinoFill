var slider = document.getElementById('range_seasons');
var output = document.getElementById('seasons_value');

let update = function() {
    output.innerHTML = slider.value
}

slider.addEventListener('input', update);
update();