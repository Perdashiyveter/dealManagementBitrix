from django.db import models
import uuid


# Create your models here.
class QRCode(models.Model):
    product_id = models.IntegerField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    photo_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f'QR для продукта {self.product_id} ({self.uuid}'

