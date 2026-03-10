from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category_id = models.IntegerField(null=True, blank=True)
    # THÊM ĐÚNG DÒNG NÀY (Lưu link ảnh từ trên mạng)
    image_url = models.URLField(max_length=1000, null=True, blank=True)