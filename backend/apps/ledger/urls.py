from django.urls import path
from .views import BalanceView

urlpatterns = [
    path("balance/<int:merchant_id>/", BalanceView.as_view()),
]