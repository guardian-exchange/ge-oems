from django.db import models

class Stock(models.Model):
    stock_id = models.AutoField(primary_key=True)
    stock_name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.stock_name
