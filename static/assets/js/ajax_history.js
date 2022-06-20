$(document).ready(function (){
    let url_path = $(location).attr('pathname')
    let btn = $('#test_button')
    let list_cards = $('.Cards')
    let loading_content = $('.next_product_more')
    let flag_load = true
    let add_history_btn = $('.Card-btn[data-history_item_pk]')
    let item_pk_new = null
    let first_btn = true



//===================================================================== ФУНКЦИИ ======================================

        // Добавляет иконку загрузки и скрывает кнопку "показать еще"
    function start_wait_ajax(){
        btn.hide()
        loading_content.append(`
        <div><img width="26" height="26" src="/static/assets/img/icons/loading/load.gif"></div>
        `)
    }

     // Добавляет кнопку "показать еще" и скрывает иконку загрузки
    function end_wait_ajax(){
        $('.next_product_more img').remove()
        if (flag_load){
            btn.show()
        } else {
             btn.remove()
        }
    }

    // после нажатия на кнопку "Показать еще"
    btn.click(function (){
        //Запуск иконки загрузки пока выполняется ajax запрос
        start_wait_ajax()
        let add_item = $('.Card').length

          $.ajax({
                url: url_path,
                method:'POST',
                dataType: 'json',
                data: {add_item: add_item,
                csrfmiddlewaretoken: btn.val(),
              },
              cache: false,
                success: function (response) {
                    let products = (response.products)
                    add_product(products);
                            // Обновляем кнопки после добавления элементов
                            $('.Card-btn[data-history_item_pk]').click(function (e){
                                e.preventDefault()
                                item_pk_new = $(this).data('history_item_pk')
                                console.log(item_pk_new)
                            })
                    if (response.flag_items_complete){
                        // флаг, что все загрузили и кнопка больше ненужна
                        flag_load = false
                    }
                    //ajax запрос выполнен и теперь уберем иконку загрузки и вернем кнопку на место
                    end_wait_ajax();
                    // обновим новые кнопки
                },
                error: function () {
                        console.log("error");
                        }
        })
    })

        // функция добавляет еще товары на страницу
    function add_product(element){
        for (let i=0; i<element.length; i++){
            let item = element[i]
            let name = item.name
            let price = item.price
            let category = item.category
            let photo = item.photo
            let item_pk = item.item_pk

                list_cards.append(`
                     <div class="Card">
                            <a class="Card-picture" href="http://127.0.0.1:8000/products/product_detail/${item_pk}/"><img src="${photo}"/></a>
                          <div class="Card-content">
                            <strong class="Card-title"><a href="http://127.0.0.1:8000/products/product_detail/${item_pk}/">${name}</a>
                            </strong>
                                <div class="Card-description">
                                       <div class="Card-cost"><span class="Card-priceOld">${price}</span><span class="Card-price">$85.00</span>
                                      </div>
                                    <div class="Card-category">${category}
                                    </div>
        
                                  <div class="Card-hover"><a class="Card-btn" data-history_item_pk = ${item_pk} href="#"><img src="/static/assets/img/icons/card/bookmark.svg" alt="bookmark.svg"/></a><a class="Card-btn" href="#"><img src="/static/assets/img/icons/card/cart.svg" alt="cart.svg"/></a><a class="Card-btn" href="#"><img src="/static/assets/img/icons/card/change.svg" alt="change.svg"/></a>
                                  </div>
                                </div>
                          </div>
                          <div class="Card-sale">-60%</div>
                        </div>
                `);
            }
    }

// ============================================КОНЕЦ ФУНКЦИЙ==========================================================

          // Тут при нажатии на кнопку с атрибутом data-history_item_pk, показывает pk - этого товара
    if (first_btn){
        add_history_btn.click(function (e){
            e.preventDefault()
            let item_pk = $(this).data('history_item_pk')
            console.log(item_pk)
            // ТУТ ajax ФУНКЦИЯ на добавление в история просмотра пользователя
            first_btn= false
        })
    }

// =======================================================КОНЕЦ JS ===================================================
});