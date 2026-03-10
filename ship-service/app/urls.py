from django.urls import path
from .views import ShipOrder, ShippingMethodList

urlpatterns = [
    path('shippings/', ShipOrder.as_view()),
    path('shipping-methods/', ShippingMethodList.as_view()),
]