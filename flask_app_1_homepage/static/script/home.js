var socket = io();

$('#predict_button').click(function () {
    raw_text = $("#review_text").val();
    socket.emit('get_prediction', { raw_text: raw_text });
});



 


socket.on('receive_prediction', function (data) {
    // convert star_pred to integer
    star_pred = parseInt(data.star_pred);
    
    for (i = 1; i <= 5; i++) {
        if (i <= star_pred) {
            $('#star_' + i).attr('src', 'static/images/star_on.svg');
        } else {
            $('#star_' + i).attr('src', 'static/images/star_off.svg');
        }
    }
        
    $("#card_course").html(data['course_pred']);
    $("#card_raw_text").html(data['raw_text']);
    $("#card_tokens").html(data['tokens']);

    // make prediction_container visible
    $(".prediction_container").css("visibility", "visible");

});