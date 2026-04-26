from django.urls import path
from .views import BalanceView
from .views import SeedBalanceView

urlpatterns = [
    path("balance/<int:merchant_id>/", BalanceView.as_view()),
    path("seed/", SeedBalanceView.as_view()),
]