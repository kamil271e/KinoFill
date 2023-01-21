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
    $('#actors_table').DataTable({
        columns: [
            null,
            {searchable: false},
            null,
            {searchable: false},
            null
        ],
    });
    $('#directors_table').DataTable({
        columns: [
            null,
            {searchable: false},
            null,
            {searchable: false},
            null
        ],
    });
    $('#studios_table').DataTable({
        columns: [
            null,
            null,
            {searchable: false},
            {searchable: false}
        ],
    });
    $('#journalists_table').DataTable({
        columns: [
            null,
            null,
            {searchable: false}
        ],
    });
    $('#news_table').DataTable({
        columns: [
            null,
            null,
            {searchable: false},
            {searchable: false, orderable: false},
            {searchable: false, orderable: false},
        ],
    });
    $('#series_roles_table').DataTable({
        columns: [
            null,
            null,
            {searchable: false}
        ],
    });
    $('#movie_roles_table').DataTable({
        columns: [
            null,
            null,
            {searchable: false}
        ],
    });
    $('#v_reviews').DataTable({
        columns: [
            null,
            {searchable: false},
            null,
            {searchable: false},
            {searchable: false, orderable: false}
        ],
    });
    $('#j_reviews').DataTable({
        columns: [
            null,
            {searchable: false},
            null,
            {searchable: false},
            {searchable: false},
            {searchable: false, orderable: false}            
        ],
    });
    $('#director_movie_table').DataTable({
        columns: [
            null,
            {searchable: false},
            {searchable: false},
            {searchable: false}         
        ],
    });
    $('#director_series_table').DataTable({
        columns: [
            null,
            {searchable: false},
            {searchable: false},
            {searchable: false}         
        ],
    });
    $('#studio_movies_table').DataTable({
        columns: [
            null,
            {searchable: false},
            {searchable: false},
            null,
            {searchable: false}         
        ],
    });
    $('#studio_series_table').DataTable({
        columns: [
            null,
            {searchable: false},
            {searchable: false},
            null,
            {searchable: false}         
        ],
    });
    $('#studio_actors_table').DataTable({
        columns: [
            null,
            {searchable: false},
            null,
            {searchable: false}         
        ],
    });
    $('#studio_directors_table').DataTable({
        columns: [
            null,
            {searchable: false},
            null,
            {searchable: false}         
        ],
    });
    $('#user_review_movies_table').DataTable({
        columns: [
            null,
            {searchable: false},
            null,
            {searchable: false}         
        ],
    });
    $('#user_review_series_table').DataTable({
        columns: [
            null,
            {searchable: false},
            null,
            {searchable: false}         
        ],
    });
    $('#user_review_actors_table').DataTable({
        columns: [
            null,
            {searchable: false},
            null,
            {searchable: false}         
        ],
    });
});

