window.onload = showDetails()

function showDetails() {
    var role = document.getElementById("role").selectedOptions[0].value
    var viewer_role = document.getElementById("viewer_role").selectedOptions[0].value
//    console.log(role)
    if(role == "Viewer") {
        document.getElementById("viewer_role_div").style.display = 'block'
        if(viewer_role == "Public") {
            document.getElementById("name_div").style.display = 'block'
        } else {
            document.getElementById("name_div").style.display = 'none'
        }
    }
    else if(role == "Journalist" || role == "Studio"){
        document.getElementById("viewer_role_div").style.display = 'none'
        document.getElementById("name_div").style.display = 'block'
    }
}