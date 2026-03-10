from django.urls import path
from .views import SubmitReview

urlpatterns = [
    path('reviews/', SubmitReview.as_view()),
]