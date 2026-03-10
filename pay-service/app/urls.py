from django.urls import path
from .views import ProcessPayment, PaymentMethodList

urlpatterns = [
    path('payments/', ProcessPayment.as_view()),
    path('payment-methods/', PaymentMethodList.as_view()),
]