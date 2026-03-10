from django.urls import path
from .views import CategoryManager

urlpatterns = [
    path('categories/', CategoryManager.as_view()),
]