from django.urls import path
from .views import GetRecommendations

urlpatterns = [
    path('ai-suggest/', GetRecommendations.as_view()),
]