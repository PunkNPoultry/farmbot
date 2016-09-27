from django.db import models

# Create your models here.
class Item(models.Model):
    name = models.CharField('item name', max_length=100)
    unit = models.CharField(max_length=50)
    price = models.DecimalField('price per unit', max_digits=6, decimal_places=2)
    quantity = models.PositiveIntegerField('quantity on hand', default=0)
    description = models.TextField(default='')
    updated_at = models.DateTimeField('inventory last updated at')

    def __str__(self):
        return self.name
