django.jQuery(document).ready(function ($) {
    $("#id_place_types").change(function () {
        $("#id_block_place_types").attr('checked', 'checked');
    });
    $("#id_name").change(function () {
        $("#id_block_name").attr('checked', 'checked');
    });
});
