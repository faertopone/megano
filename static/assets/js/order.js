$(document).ready(function () {
    let url_path = $(location).attr('pathname')
    let crsf = ($('input[name="csrfmiddlewaretoken"]').val())
    let total_price_val = Number($('#total_price').attr('data-price'))
    let btn_step = $('.Order-next[href="#step4"]')
    let total = 0
     let total_price = 0
        // перед шагом, соберем всю инфу и выведем перед оканчательным заказом
    if (btn_step){
          btn_step.click(function (){
              // Получим данные которые ввел пользователь
              let first_name = $('input[name="first_name"]').val()
              let email = $('input[name="email"]').val()
              let last_name = $('input[name="last_name"]').val()
              let city = $('input[name="city"]').val()
              let patronymic = $('input[name="patronymic"]').val()
              let phone = $('input[name="phone"]').val()
              let delivery = $('input:checked[name="delivery"]').val()
              let payment = $('input:checked[name="payment"]').val()
              let address = $('input[name="address"]').val()

                  // Обновим на последней странице данные
              $('#FIO').text(first_name + ' ' + last_name + ' '+ patronymic)
              $('#email').text(email)
              $('#phone').text(phone)
              $('#delevery').text(delivery)
              $('#city').text(city)
              $('#address').text(address)
              $('#pay').text(payment)

              $.ajax({
                url: url_path,
                method:'POST',
                dataType: 'json',
                data:
                    {csrfmiddlewaretoken: crsf
                    },
              cache: false,
                success: function (data) {

                    let price_delivery = data.price_delivery
                    let delivery_price = data.delivery_price
                     // если выбрана экспресс доставка +500р
                      if (delivery === 'Экспресс доставка'){
                           delivery_price += price_delivery
                      }
                                            // сумма с доставкой
                      total = total_price_val + delivery_price
                      $('#total_price').text(total.toString() + ' руб.')

                      $('#total_price').append(`
                      <div class="Section-content"> Доставка: ${delivery_price} руб.</div>
                      `)


                },
                error: function () {
                        console.log("error");
                        }
        })



          })
    }

})