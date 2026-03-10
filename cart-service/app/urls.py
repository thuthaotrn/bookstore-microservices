from django.urls import path
from .views import CartCreate, AddCartItem, ViewCart, ManageCartItem

urlpatterns = [
    # API tạo giỏ hàng mới
    path('carts/', CartCreate.as_view()),
    
    # API thêm sách vào giỏ
    path('cart-items/', AddCartItem.as_view()),
    
    # API xem giỏ hàng của một khách cụ thể
    path('carts/<int:customer_id>/', ViewCart.as_view()),

    # Thêm dòng này để update số lượng sách trong giỏ
    path('cart-items/<int:item_id>/', ManageCartItem.as_view()),
]