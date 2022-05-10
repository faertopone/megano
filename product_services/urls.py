from django.urls import path
from .views import HistoryView, ProductComment, ProductComparison


urlpatterns = [
    path('historyview', HistoryView.as_view(), name='history view'),
    path('product/<int:pk>/comment', ProductComment.as_view(), name='product comment'),
    path('product/<int:pk>/comparison', ProductComparison.as_view(), name='product comparison')
]
