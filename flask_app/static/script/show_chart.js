
document.addEventListener('selectionchange', (e) => {
    word = window.getSelection().toString();
    if (word != '') {
        socket.emit('request_word_usage_chart', word);
    }

});


$('.popupCloseButton').click(function () {
    $('.hover_bkgr_fricc').hide();
});



socket.on('place_word_usage_chart', function (word) {
    $('#word_chart').val('')
    if (word != '') {

        // join '/static/images/word_usage/' and word and '.png'
        url_path = ['url(.', word].join('/');

        $('#word_chart_div').css('background-image', url_path);

        $('.hover_bkgr_fricc').show();
        $('#word_chart_div').css('background-image', url_path);
    }
});


socket.on('place_filtered_data', function (response) {
    $('.table tbody').replaceWith(response);
    $('#rowcount').text($('.table').find('tbody').find('tr').length);
});