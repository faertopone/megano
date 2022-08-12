$(document).ready(function (){
  let add_button = $('#add-button')
  let url_path ='/basket/add/'
  let crsf = ($('input[name="csrfmiddlewaretoken"]').val())
  let all_add_button = $('.add-button')
        add_button.click(function (e) {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: url_path,
            data: {
                product_id: $('#add-button').val(),
                product_qty: $('#select').val(),
                csrfmiddlewaretoken: add_button.attr('data-csrf'),
                action: 'add'
            },
            success: function (json) {
                document.getElementById('basket-qty').innerHTML = json.qty;
                document.getElementById('h-subtotal').innerHTML = json.subtotal;
                // document.getElementById('subtotal').innerHTML = json.subtotal;
            },
            error: function (xhr, errmsg, err) {
            }
        });
    })

    all_add_button.click(function (e) {
        e.preventDefault();
        var prodid = $(this).attr('data-value');
        console.log(prodid)
        var shop_prod_id = $(this).attr('data-shop');
        console.log(shop_prod_id)
        console.log(crsf)
        $.ajax({
            type: 'POST',
            url: url_path,
            data: {
                product_id: prodid,
                product_qty: 1,
                shop_product_id: shop_prod_id,
                csrfmiddlewaretoken: crsf !== null && crsf !== undefined ? crsf : $(this).attr('data-csrf'),
                action: 'add'
            },
            success: function (json) {
                document.getElementById('basket-qty').innerHTML = json.qty;
                document.getElementById('h-subtotal').innerHTML = json.subtotal;
                // document.getElementById('subtotal').innerHTML = json.subtotal;
            },
            error: function (xhr, errmsg, err) {
            }
        });
    })

})
