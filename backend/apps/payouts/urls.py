from django.urls import path
from .views import PayoutView
from .views import FixPendingView



urlpatterns = [
    path("payouts/", PayoutView.as_view()),
    path("fix-pending/", FixPendingView.as_view()),
]