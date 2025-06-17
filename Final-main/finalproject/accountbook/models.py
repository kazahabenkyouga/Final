from django.db import models

class GmailData(models.Model):
    label = models.CharField(max_length=100)
    count = models.IntegerField()
    year = models.IntegerField()
    month = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('label', 'year', 'month')

class GmailTransaction(models.Model):
    usage_datetime = models.DateTimeField()  # ご利用日時
    amount = models.IntegerField()           # 金額（円マークなし）
    message_id = models.CharField(max_length=255, unique=True)  # 重複防止
    category = models.CharField(max_length=50, default='未分類')
    tag = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"{self.usage_datetime} - {self.amount}円"

