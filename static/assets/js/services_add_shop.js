$(document).ready(function () {

  let btn_card = $('#add-button, .add-button')
  let btn_card_text = $('#add-button .btn-content')
  // если эта кнопка есть на странице
  if (btn_card){
    btn_card.click(function (){
      btn_card_text.text('Товар добавлен')
      $(this).css('background-color', '#1f7eff')
    })
  }

})
