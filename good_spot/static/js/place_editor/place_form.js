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
            show_errors: 'always',
            disable_edit_json: true,
            disable_properties: true
        }
    );
    // draft
    // place_editor.disable();
    // place_editor.getEditor('root.google_price_level').disable();
    var cust_err = [];

    $("#submit").on('click', function () {
        console.log('submit');

        cust_err = [];

        $.ajax({
            url: url,
            method: 'POST',
            data: place_editor.getValue()
        }).done(function (data) {
            console.log('DONE');
            var place_edit_url = dutils.urls.resolve('admin_place_editor', {id: data['id']});
            window.location.href = place_edit_url;

        }).fail(function (data) {
            console.log('FAIL');
            for (var i in data.responseJSON) {
                cust_err.push({
                    path: 'root.' + i,
                    property: 'minLength',
                    message: data.responseJSON[i]
                });
            }
            var errors = place_editor.validate();
            place_editor.getEditor('root.google_place_id').change();
        });

    });


    JSONEditor.defaults.custom_validators.push(function (schema, value, path) {
        var errors = [];
        for (var i in cust_err) {
            if (path == cust_err[i]['path']) {
                errors = cust_err;
            }
        }
        return errors;
    });


});
