django.jQuery(document).ready(function ($) {
    var rendered_element_container = ".rendered-place-field-value";
    var dynamic_place_fields_class = ".dynamic-place_fields";
    var tmp_value_class = ".tmp_value";

    function load_field(el) {
        var place_field_id = el.find("input[id*='id_place_fields-']").val();
        if (place_field_id) {
            var render_place_field_value = "/admin/places/place/render_place_field_value/" + place_field_id + "/";

            $.ajax({
                url: render_place_field_value
            }).done(function (data) {
                el.find(rendered_element_container).html(data);
            }).fail(function (data) {
                console.log(data);
            });
        } else {
            var field_type_id = el.find('option:selected').val();
            if (field_type_id) {
                var render_field_type_value = "/admin/places/place/render_field_type_value/" + field_type_id + "/";

                $.ajax({
                    url: render_field_type_value
                }).done(function (data) {
                    el.closest(".dynamic-place_fields").find(rendered_element_container).html(data);
                }).fail(function (data) {
                    console.log(data);
                });
            } else {
                el.closest(".dynamic-place_fields").find(rendered_element_container).html("");
            }
        }
    }


    $(dynamic_place_fields_class).each(function (i) {
        var el = $(this);
        load_field(el);
    });

    $(".place-field-inline-form-row .field-field_type select[id*='id_place_fields']").change(function () {
        var el = $(this);
        var field_type_id = el.find('option:selected').val();
        if (field_type_id) {
            var render_field_type_value = "/admin/places/place/render_field_type_value/" + field_type_id + "/";

            $.ajax({
                url: render_field_type_value
            }).done(function (data) {
                el.closest(".dynamic-place_fields").find(rendered_element_container).html(data);
            }).fail(function (data) {
                console.log(data);
            });
        } else {
            el.closest(".dynamic-place_fields").find(rendered_element_container).html("");
        }
    });

    $("input[name='_save']").on('click', function (e) {
        e.preventDefault();

        $(dynamic_place_fields_class).each(function (i) {
            var el = $(this);
            var val;
            if (el.find(tmp_value_class).attr('type') == 'checkbox') {
                val = el.find(tmp_value_class).is(":checked");
            } else {
                val = el.find(tmp_value_class).val();
            }
            val = JSON.stringify(val);
            el.find("#id_place_fields-" + i + "-value").val(val);
        });
        $("#place_form").submit();
    });
});