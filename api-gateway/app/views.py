from django.shortcuts import render
import requests

# ==========================================
# KHU VỰC 1: CUSTOMER (KHÁCH HÀNG)
# ==========================================

# 1. Đăng ký / Đăng nhập
def auth_view(request):
    return render(request, 'login.html')

# 2. Trang chủ (Book List & AI)
def home(request):
    # Tạm thời trả về trang rỗng chờ đấu API
    return render(request, 'index.html', {'books': []})

# 3. Trang Chi tiết Sách & Review
def book_detail(request, book_id):
    # Nhận book_id từ URL để lát nữa gọi book-service
    return render(request, 'detail.html', {'book_id': book_id})

# 4. Trang Giỏ hàng
def cart_view(request):
    return render(request, 'cart.html')

# 5. Trang Chốt đơn
def checkout_view(request):
    return render(request, 'checkout.html')

# 6. Lịch sử Đơn hàng
def orders_view(request):
    return render(request, 'orders.html')


# ==========================================
# KHU VỰC 2: BACK-OFFICE (BAN QUẢN TRỊ)
# ==========================================

# 7. Quản lý kho (Staff)
def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')

# 8. Báo cáo doanh thu (Manager)
def manager_dashboard(request):
    return render(request, 'manager_dashboard.html')