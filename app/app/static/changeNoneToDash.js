window.onload = changeNone()

function changeNone() {
    const headers = document.querySelectorAll("h1, h2, h3, h4, h5, h6");
    const cells = document.querySelectorAll("td");

    for (const header of headers) {
        if(header.textContent.includes("None")) {
            header.textContent = header.textContent.replaceAll('None', '-');
        }
    }
    for (const cell of cells) {
        if(cell.textContent.includes("None")) {
            cell.textContent = cell.textContent.replaceAll('None', '-');
        }
    }
}