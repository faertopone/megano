$(document).ready(function () {

// Берём элемент для вывода таймера
let timer_show_day = $('#timer_day');
let timer_show_hour = $('#timer_hour');
let timer_show_min = $('#timer_min');
let timer_show_sec = $('#timer_sec');
let limit_day = $('#limit_day').val();

// Массив данных о времени
let end_date = {
    "full_year": "1970", // Год
    "month": "00", // Номер месяца
    "day": limit_day, // День
    "hours": "00", // Час
    "minutes": "00", // Минуты
    "seconds": "00" // Секунды
}



// Функция для вычисления разности времени
function diffSubtract(date1, date2) {
    return date2 - date1;
}








})
