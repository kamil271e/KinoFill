window.onload = showDetails()

function showDetails() {
    var viewer_role = document.getElementById("viewer_role").selectedOptions[0].value
    if(1 == 1) {
        document.getElementById("viewer_role_div").style.display = 'block'
        if(viewer_role == "Public") {
            document.getElementById("public_div").style.display = 'block'
        } else {
            document.getElementById("public_div").style.display = 'none'
        }
    }
}