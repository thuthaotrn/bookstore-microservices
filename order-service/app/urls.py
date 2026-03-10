from django.urls import path
from .views import CreateOrder, UpdateOrderStatus

urlpatterns = [
    path('orders/', CreateOrder.as_view()),
    path('orders/<int:pk>/status/', UpdateOrderStatus.as_view()),
]