$(document).ready(function () {

  let btn_card = $('#add-button, .add-button')
  let btn_card_text = $('#add-button .btn-content')
  // если эта кнопка есть на странице
  if (btn_card){
    btn_card.click(function (){
      btn_card_text.text('Товар добавлен')
    })
  };

  let btn_card_pulse = $('.add-button.add-button-pulse')
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

  let btn_compare = $('#add-compare, .add-compare')
  if (btn_compare){
    btn_compare.click(function (){
      $(this).css('background-color', '#1f7eff')
    })
  }

})
