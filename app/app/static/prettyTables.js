$(document).ready(function () {
    $('#movies_table').DataTable({
        columns: [
            null,
            {searchable: false},
            {searchable: false},
            null,
            null,
            {searchable: false}
        ],
    });
});

$(document).ready(function () {
    $('#series_table').DataTable({
        columns: [
            null,
            {searchable: false},
            {searchable: false},
            null,
            null,
            {searchable: false}
        ],
    });
});

$(document).ready(function () {
    $('#actors_table').DataTable({
        columns: [
            null,
            {searchable: false},
            null,
            {searchable: false},
            null
        ],
    });
});

$(document).ready(function () {
    $('#directors_table').DataTable({
        columns: [
            null,
            {searchable: false},
            null,
            {searchable: false},
            null
        ],
    });
});

$(document).ready(function () {
    $('#studios_table').DataTable({
        columns: [
            null,
            null,
            {searchable: false},
            {searchable: false}
        ],
    });
});

$(document).ready(function () {
    $('#journalists_table').DataTable({
        columns: [
            null,
            null,
            {searchable: false}
        ],
    });
});