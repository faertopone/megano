$(document).ready(function (){
    let url_path = $(location).attr('pathname')
    let btn = $('#test_button')
    let list_cards = $('.Cards')
    let loading_content = $('.next_product_more')
    let flag_load = true




    function start_wait_ajax(){
        btn.hide()
        loading_content.append(`
        <div><img width="26" height="26" src="/static/assets/img/icons/loading/load.gif"></div>
        `)
    }

    function end_wait_ajax(){
        $('.next_product_more img').remove()
        if (flag_load){
            btn.show()
        } else {
             btn.remove()
        }

    }


    btn.click(function (){
        //Запуск иконки загрузки пока выполняется ajax запрос
        start_wait_ajax()

        let add_item = $('.Card').length
          $.ajax({
            url: url_path,
            method:'POST',
              data: {add_item: add_item,
                  csrfmiddlewaretoken: btn.val(),
              },
              cache: false,

                success: function (response) {

                let products = (response.products)
                    add_product(products)
                    if (response.flag_items_complete){
                        // флаг, что все загрузили и кнопка больше ненужна
                        flag_load = false
                    }
                    //ajax запрос выполнен и теперь уберем иконку загрузки и вернем кнопку на место
                    end_wait_ajax()

                },
                error: function () {
                    console.log("error");
                }
        })



    })

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
        
                                  <div class="Card-hover"><a class="Card-btn" href="#"><img src="/static/assets/img/icons/card/bookmark.svg" alt="bookmark.svg"/></a><a class="Card-btn" href="#"><img src="/static/assets/img/icons/card/cart.svg" alt="cart.svg"/></a><a class="Card-btn" href="#"><img src="/static/assets/img/icons/card/change.svg" alt="change.svg"/></a>
                                  </div>
                                </div>
                          </div>
                          <div class="Card-sale">-60%</div>
                        </div>
                `);
            }
    }

});