from django.urls import path

from .views import PromotionListView, PromotionDetailView


app_name = "promotions"

urlpatterns = [
    path("", PromotionListView.as_view(), name="promotion_list"),
    path("<int:pk>/", PromotionDetailView.as_view(), name="promotion_detail"),
]
