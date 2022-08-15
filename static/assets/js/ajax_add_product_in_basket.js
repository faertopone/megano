$(document).ready(function (){
  let add_button = $('#add-button')
  let url_path ='/basket/add/'
  let crsf = ($('input[name="csrfmiddlewaretoken"]').val())
  let all_add_button = $('.add-button')
  let btn = $('#test_button')
  let btn_card = $('#add-button, .add-button')
  let btn_card_text = $('#add-button .btn-content')
  let btn_compare = $('#add-compare, .add-compare')
  let btn_card_pulse = $('.add-button.add-button-pulse')

  function color_button(){
     // если эта кнопка есть на странице
    if (btn_card){
      btn_card.click(function (){
        btn_card_text.text('Товар добавлен')
      })
    }

    if (btn_card_pulse) {
      btn_card_pulse.click(function (){
        // добавить класс анимации
        $(this).addClass("add-button-pulse-anim")
        // анимация на js
        $(this).animate({
          backgroundColor: "#ebebeb",
        }, 3000, function() {
          // анимация завершена.
          // удалить класс анимации
          $(this).removeClass("add-button-pulse-anim")
        });
      })
    }

    if (btn_compare){
      btn_compare.click(function (){
        $(this).css('background-color', '#1f7eff')
      })
    }
  }



  if (btn) {
    btn.click(function (e) {
       e.preventDefault()
         // логика добавления в корзину после нажатия кнопки в истории просмотров _ показать еще
      setTimeout(function () {
        btn_card = $('#add-button, .add-button')
        btn_compare = $('#add-compare, .add-compare')
        all_add_button = $('.add-button')

        color_button()
        compare()

        all_add_button.click(function (e) {
        e.preventDefault();
        var prodid = $(this).attr('data-value');
        var shop_prod_id = $(this).attr('data-shop');
          $.ajax({
              type: 'POST',
              url: url_path,
              data: {
                  product_id: prodid,
                  product_qty: 1,
                  shop_product_id: shop_prod_id,
                  csrfmiddlewaretoken: crsf,
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
        }, 1000);
      })
  }


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
        var shop_prod_id = $(this).attr('data-shop');
        console.log(shop_prod_id)
        console.log(crsf)

        $.ajax({
            type: 'POST',
            url: url_path,
            data: {
                product_id: prodid,
                product_qty: $('.select' + shop_prod_id).val(),
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

   function compare(){
    $(".Card-change").click(function () {
        var productId = $(this).data('product');
        var cacheKey = $(this).data('key')
        $.ajax ({
            url: "/products/count_compare_add/",
            type: "GET",
            data: {'product': productId, 'cache_key': cacheKey
            },
            cache: false,
            success: function (data) {
                console.log('ok');
                console.log(data.com_count);
                console.log(productId, cacheKey);
                $('#compare_count_id').text(data.com_count);
                },
            error: function() {
                console.log('error');
                console.log(productId, cacheKey);
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

    $(".expand").magnificPopup({
      type: "image"
    });

    $("#category_id").click(function () {
    var sh_id = document.getElementById("selshop").value;
    var cat_id = document.getElementById("selcategory").value;
        $.ajax ({
            url: "/import/ajax/",
            type: "GET",
            data: {'shop': sh_id, 'category': cat_id
            },
            cache: false,
            success: function (data) {
                console.log('ok');
                console.log(data);
                $('#category_list').html(data.text);
                document.getElementById('update').style.display='block';
                document.getElementById('file_button').value=data.shop_id + '|' + data.category_id;
                document.getElementById('file').href='/import/export/' + data.category_id
                },
            error: function() {
                console.log('error')
                }
        });
        return false;
    });
   }

  compare()
  color_button()

})
