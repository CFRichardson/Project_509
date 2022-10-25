var socket = io();

// when document is loaded count number of .table tbody tr
$(document).ready(function () {
    $('#rowcount').text($('.table').find('tbody').find('tr').length);
});



// when button 'btn-filter' in docuemnt is clicked then alert 'filter' will be shown
$(document).on('click', '.btn-filter', function () {
    toggle_header_filters();
});

function toggle_header_filters() {
    // check if first $('.filters').find('input') enable to edit
    if ($('.filters').find('input').is(':disabled')) {
        $('.filters').find('input').prop('disabled', false);
    }
    else {
        $('.filters').find('input').prop('disabled', true);
    }
};

// when enter is pressed when input in filters then
$(document).on('keypress', '.filters', function (e) {
    if (e.which == 13) {

        request_data = {
            "id": $('#header_id').val(),
            "course_name": $('#header_course_name').val(),
            "star": $('#header_star').val(),
            "text": $('#header_text').val(),
        }

        socket.emit('get_filtered_data', request_data)

    }
});


function show_rows_that_meet_filter_conditions
    (header_values) {
    var rowcount = 0;

    // get all rows in table
    var rows = $('.table').find('tbody').find('tr');
    // for each row 
    rows.each(function (index, row) {
        // get all cells in row
        var id_value = $(row).find('td').eq(0).text();
        var course_name_value = $(row).find('td').eq(1).text();
        var star_value = $(row).find('td').eq(2).text();
        var text_value = $(row).find('td').eq(3).text();
        // list of words in header_values['text'] split by space if exits
        var tokens_to_search = [];
        if (header_values['text'] != undefined) {
            tokens_to_search = header_values['text'].split(' ');
        }
        // if _value contrain header_values then show row (skip empty header_values)
        if (
            (header_values['id'] == undefined || id_value.includes(header_values['id'])) &&
            (header_values['course_name'] == undefined || course_name_value.includes(header_values['course_name'])) &&
            (header_values['star'] == undefined || star_value.includes(header_values['star'])) &&
            (header_values['text'] == undefined || tokens_to_search.every(function (token) {
                return text_value.includes(token);
            }))) {
            $(row).show();
            rowcount++;
        }
        else {
            $(row).hide();
        }
    });


    // set value of id='rowcount' to rowcount
    $('#rowcount').text(rowcount);
};


