django.jQuery(document).ready(function ($) {
    function load_field(el) {
        var field_type_id = $(el).find('option:selected').val();
        var get_field_type_url = '/admin/places/place/get_field_type/' + field_type_id + '/';

        $.ajax({
            url: get_field_type_url
        }).done(function (data) {
            var field_type = data['field_type'];
            var element_name = "tmp_value";
            var new_element;

            if (field_type == 'bool') {
                new_element = $('<input />', {
                        type: 'checkbox',
                        id: 'id_' + element_name,
                        name: element_name
                    }
                );
                if ($("#id_value").val() == 'true') {
                    new_element.attr('checked', 'checked');
                }
            } else if (field_type == 'text') {
                new_element = $('<textarea />', {
                    id: 'id_' + element_name,
                    name: element_name
                });
                if ($("#id_value").val() != 'null') {
                    new_element.text($("#id_value").val());
                }
            } else if (field_type == 'multi') {
                new_element = $('<select />', {
                    id: 'id_' + element_name,
                    name: element_name,
                    multiple: "multiple"
                });
                $(data['data']).each(function () {
                    if ($("#id_value").val().includes(this)) {
                        new_element.append($("<option selected>").attr('value', this).text("--- " + this));
                    } else {
                        new_element.append($("<option>").attr('value', this).text("--- " + this));
                    }
                });
            } else if (field_type == 'choice') {
                new_element = $('<select />', {
                    id: 'id_' + element_name,
                    name: element_name
                });
                $(data['data']).each(function () {
                    if ($("#id_value").val().includes(this)) {
                        new_element.append($("<option selected>").attr('value', this).text(this));
                    } else {
                        new_element.append($("<option>").attr('value', this).text(this));
                    }
                });
            } else if (field_type != null) {
                new_element = "Unexpected field type."
            }
            $("#id_dynamic_field").html(new_element);
        }).fail(function (data) {
            console.log(data);
        });
    }

    load_field($("#id_field_type"));

    $("#id_field_type").change(function () {
        load_field(this);
    });

    $("input[name='_save']").on('click', function (e) {
        e.preventDefault();
        var val;
        if ($("#id_tmp_value").attr('type') == 'checkbox') {
            val = $("#id_tmp_value").is(":checked");
        } else {
            val = $("#id_tmp_value").val();
        }
        val = JSON.stringify(val);
        $("#id_value").val(val);
        $("#placefield_form").submit();
    });
});