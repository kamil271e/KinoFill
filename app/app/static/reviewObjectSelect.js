window.onload = objectSelect()

function objectSelect() {
    var type = document.getElementById("review_object_type").selectedOptions[0].value
    var movies = document.getElementById("movie_select")
    var series = document.getElementById("series_select")
    var actors = document.getElementById("actors_select")

    if (type == "Series") {
        movies.style.display = 'none'
        series.style.display = 'block'
        actors.style.display = 'none'
    } else if (type == "Movie") {
        movies.style.display = 'block'
        series.style.display = 'none'
        actors.style.display = 'none'
    } else if (type == "Actor") {
        movies.style.display = 'none'
        series.style.display = 'none'
        actors.style.display = 'block'
    }
}