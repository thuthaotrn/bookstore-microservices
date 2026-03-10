from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Định tuyến Khách hàng ---
    path('', views.home, name='home'),                                 # http://localhost:8000/
    path('auth/', views.auth_view, name='auth'),                       # http://localhost:8000/auth/
    path('book/<int:book_id>/', views.book_detail, name='book_detail'), # http://localhost:8000/book/2/
    path('cart/', views.cart_view, name='cart'),                       # http://localhost:8000/cart/
    path('checkout/', views.checkout_view, name='checkout'),           # http://localhost:8000/checkout/
    path('orders/', views.orders_view, name='orders'),       
    # Đường dẫn trang Đăng nhập
    path('login/', views.login_view),          # http://localhost:8000/orders/
    
    # --- Định tuyến Ban quản trị ---
    path('staff/', views.staff_dashboard, name='staff_dashboard'),     # http://localhost:8000/staff/
    path('manager/', views.manager_dashboard, name='manager_dashboard'),# http://localhost:8000/manager/

    # ĐƯỜNG HẦM VẠN NĂNG (Hứng mọi thể loại API từ Frontend)
    # Cấu trúc: /api/<tên_service>/<đường_dẫn_thực_tế>
    path('api/<str:service_name>/<path:path>', views.universal_proxy),
]