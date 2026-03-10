from django.db import models

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100) # Tên (VD: Thanh toán khi nhận hàng)
    code = models.CharField(max_length=50)  # Mã (VD: COD, CREDIT_CARD)

class Payment(models.Model):
    order_id = models.IntegerField()
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    amount = models.FloatField()
    status = models.CharField(max_length=50, default="PENDING")