$(document).ready(function () {

    var place_editor = new JSONEditor(
        document.getElementById("place_editor_holder"),
        {
            schema: {
                title: "Place",
                type: "object",
                id: "place",
                properties: properties
            },
            startval: initial_data,
            show_errors: 'never',
            no_additional_properties: true,
            disable_edit_json: true,
            disable_properties: true
        }
    );

    // draft
    // place_editor.disable();
    // place_editor.getEditor('root.google_price_level').disable();

    $("#submit").on('click', function () {
        // for (var el in document.getElementsByName('root[google_price_level]')){
        //     place_editor.theme.removeInputError(document.getElementsByName('root[google_price_level]')[el]);
        // }
        cust_err = [];
        $.ajax({
            url: url,
            method: 'PATCH',
            data: JSON.stringify(place_editor.getValue()),
            contentType: 'application/json'
        }).done(function (data) {
            window.location.reload();
        }).fail(function (data) {
            // alert('Something went wrong. Check errors near the fields.')
            for (var i in data.responseJSON) {
                place_editor.theme.addInputError(
                    document.getElementsByName('root[' + i + ']')[0],
                    data.responseJSON[i]
                );
            }
        });
    });

    $("#submit_and_quit").on('click', function () {
        cust_err = [];
        $.ajax({
            url: url,
            method: 'PATCH',
            data: JSON.stringify(place_editor.getValue()),
            contentType: 'application/json'
        }).done(function (data) {
            var place_list_url = dutils.urls.resolve('admin_place_list');
            window.location.href = place_list_url;
        }).fail(function (data) {
            // alert('Something went wrong. Check errors near the fields.')
            for (var i in data.responseJSON) {
                place_editor.theme.addInputError(
                    document.getElementsByName('root[' + i + ']')[0],
                    data.responseJSON[i]
                );
            }
        });
    });

    $("#add_another").on('click', function () {
        var place_new_add = dutils.urls.resolve('admin_place_add');
        window.location.href = place_new_add;
    });

    var block_name = place_editor.getEditor('root.block_name');
    place_editor.watch('root.name_en', function () {
        block_name.setValue(true);
    });
    place_editor.watch('root.name_fr', function () {
        block_name.setValue(true);
    });
    place_editor.watch('root.name_ru', function () {
        block_name.setValue(true);
    });

    place_editor.watch('root.name_uk', function () {
        block_name.setValue(true);
    });

    var block_place_types = place_editor.getEditor('root.block_place_types');
    place_editor.watch('root.place_types', function () {
        block_place_types.setValue(true);
    });

});
