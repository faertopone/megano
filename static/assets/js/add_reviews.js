$(document).ready(function () {
    $("#UserReviewForm").submit(function (e) {
        e.preventDefault()
        $.ajax({
            method: 'POST',
            headers: {"X-CSRFToken": this.csrfmiddlewaretoken.value},
            dataType: 'json',
            data: {review: this.review.value},
            cache: false,
            success: function (response) {
                let review = response["review"]
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
                $("#count-reviews-1").html(`Отзывов (${review.reviews_count})`)
                $("#count-reviews-2").html(`${review.reviews_count} Отзывов`)
                $("#UserReviewForm")[0].reset();
            },
            error: function (response) {
                console.log(response)
            }
        });
    });
});