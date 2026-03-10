from django.contrib import admin
from django.urls import path, include  # <-- Chỗ này cực kỳ dễ quên chữ 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
]