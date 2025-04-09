from django.db import models
from django.contrib.auth.models import AbstractUser
from stocks.models import Stock

class User(AbstractUser):
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.username

class UserStock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stocks")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ("user", "stock")
