$(document).ready(function () {
    $("#compare_id").click(function () {
        $.ajax ({
            url: "/products/count_compare_add/",
            type: "GET",
            data: {'product_info': $("#compare_id").val()
            },
            cache: false,
            success: function (data) {
                console.log('ok');
                console.log(data.com_count);
                $('#compare_count_id').text(data.com_count);
                },
            error: function() {
                console.log('error')
                }
        });
        return false;
    });

    $(".Compare-checkDifferent input").click(function () {
        $('#full').toggle();

        return {
            init: function(){
                $checkDifferent.trigger('change');
            }
        };

    });

    $("#basket").click(function () {
        $.ajax ({
            url: "/products/compare_basket/",
            type: "GET",
            dataType: "text",
            cache: false,
        });
        return false;
    });
})