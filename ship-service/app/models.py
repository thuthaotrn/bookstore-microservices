from django.db import models

class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)      # Tên (VD: Giao hỏa tốc)
    fee = models.FloatField(default=0.0)         # Phí ship
    description = models.CharField(max_length=255) # Mô tả

# Bảng này để dành cho bước lưu đơn hàng
class Shipment(models.Model):
    order_id = models.IntegerField()
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL, null=True)
    address = models.TextField()
    status = models.CharField(max_length=50, default="PENDING")