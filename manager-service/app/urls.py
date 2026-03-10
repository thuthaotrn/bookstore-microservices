from django.urls import path
from .views import GenerateReport

urlpatterns = [
    path('reports/', GenerateReport.as_view()),
]