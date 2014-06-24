$(document).ready(function() {
    var check_random_type = function(event) {
        var random_type = $('#id_random_type').val();
        $('.field-range_min, .field-range_max, .field-random_set').hide();
        if (random_type === 'numeric') {
            $('.field-range_min, .field-range_max').show();
        } else if (random_type === 'string') {
            $('.field-random_set').show();
        }
    };
    check_random_type();
    $('#id_random_type').on('change', check_random_type);
});
