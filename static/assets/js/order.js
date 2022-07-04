$(document).ready(function () {
    let btn_step = $('.Order-next[href="#step4"]')
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

          })
    }

})