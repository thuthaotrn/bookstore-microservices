from django.db import models

class AI_Log(models.Model):
    customer_id = models.IntegerField()
    recommended_book_id = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)