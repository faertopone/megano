(function ($) {
    $('#lazy_load_reviews').on('click', function () {
        let link = $(this);
        let page = link.data('page');
        let product_id = $(this).val()
        $.ajax({
            type: 'get',
            url: 'http://127.0.0.1:8000/products/lazy_load_reviews/',
            data: {
                'skip': page,
                "product_id": product_id
            },
            success: function (response) {
                let reviews = response["reviews"];
                reviews.forEach((review) => {
                    $("#insert_reviews").before(`
                        <div class="Comments">
                            <div class="Comment">
                                <div class="Comment-column Comment-column-pict">
                                    <div class="Comment-avatar">
                                        <img width="90" height="75" src="${review.client_photo}" alt="${review.photo_name}">
                                    </div>
                                </div>
                                <div class="Comment-column">
                                    <header class="Comment-header">
                                        <div>
                                            <strong class="Comment-title">${review.user}</strong>
                                            <span class="Comment-date">${review.created_at}</span>
                                        </div>
                                    </header>
                                    <div class="Comment-content">
                                        ${review.review}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `);
                });
            },
            error: function (xhr, status, error) {
                console.log(error)
            }
        });
    });
}(jQuery));