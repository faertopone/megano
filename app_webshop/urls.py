from django.urls import path, include

from .views import Index
from .services.views import HistoryView, ProductComment

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('historyview', HistoryView.as_view(), name='history view'),
    path('product/<int:pk>/comment', ProductComment.as_view(), name='product comment'),
]
