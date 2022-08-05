$(document).ready(function () {

  let btn_card = $('#add-button')
  let btn_card_text = $('#add-button .btn-content')
  // если эта кнопка есть на странице
  if (btn_card){
    btn_card.click(function (){
      btn_card_text.text('Товар добавлен в корзину')
      $(this).css('background-color', 'green')
    })
  }

})
