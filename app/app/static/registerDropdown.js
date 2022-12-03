window.onload = showDetails()

function showDetails() {
    var role = document.getElementById("role").selectedOptions[0].value
    var viewer_role = document.getElementById("viewer_role").selectedOptions[0].value
//    console.log(role)
    if(role == "Widz") {
        document.getElementById("viewer_role_div").style.display = 'block'
        if(viewer_role == "Publiczne") {
            document.getElementById("name_div").style.display = 'block'
        } else {
            document.getElementById("name_div").style.display = 'none'
        }
    }
    else if(role == "Dziennikarz" || role == "Wytwórnia filmowa"){
        document.getElementById("viewer_role_div").style.display = 'none'
        document.getElementById("name_div").style.display = 'block'
    }
}