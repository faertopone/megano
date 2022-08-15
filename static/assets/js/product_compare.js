// $(document).ready(function () {
// //    $("#compare_id").click(function () {
// //        $.ajax ({
// //            url: "/products/count_compare_add/",
// //            type: "GET",
// //            data: {'product_info': $("#compare_id").val()
// //            },
// //            cache: false,
// //            success: function (data) {
// //                console.log('ok');
// //                console.log(data.com_count);
// //                $('#compare_count_id').text(data.com_count);
// //                },
// //            error: function() {
// //                console.log('error')
// //                }
// //        });
// //        return false;
// //    });
//
//     $(".Card-change").click(function () {
//         var productId = $(this).data('product');
//         var cacheKey = $(this).data('key')
//         $.ajax ({
//             url: "/products/count_compare_add/",
//             type: "GET",
//             data: {'product': productId, 'cache_key': cacheKey
//             },
//             cache: false,
//             success: function (data) {
//                 console.log('ok');
//                 console.log(data.com_count);
//                 console.log(productId, cacheKey);
//                 $('#compare_count_id').text(data.com_count);
//                 },
//             error: function() {
//                 console.log('error');
//                 console.log(productId, cacheKey);
//                 }
//         });
//         return false;
//     });
//
//     $(".Compare-checkDifferent input").click(function () {
//         $('#full').toggle();
//         return {
//             init: function(){
//                 $checkDifferent.trigger('change');
//             }
//         };
//
//     });
//
//     $("#basket").click(function () {
//         $.ajax ({
//             url: "/products/compare_basket/",
//             type: "GET",
//             dataType: "text",
//             cache: false,
//         });
//         return false;
//     });
//
//     $(".expand").magnificPopup({
//       type: "image"
//     });
//
//     $("#category_id").click(function () {
//     var sh_id = document.getElementById("selshop").value;
//     var cat_id = document.getElementById("selcategory").value;
//         $.ajax ({
//             url: "/import/ajax/",
//             type: "GET",
//             data: {'shop': sh_id, 'category': cat_id
//             },
//             cache: false,
//             success: function (data) {
//                 console.log('ok');
//                 console.log(data);
//                 $('#category_list').html(data.text);
//                 document.getElementById('update').style.display='block';
//                 document.getElementById('file_button').value=data.shop_id + '|' + data.category_id;
//                 document.getElementById('file').href='/import/export/' + data.category_id
//                 },
//             error: function() {
//                 console.log('error')
//                 }
//         });
//         return false;
//     });
// })
