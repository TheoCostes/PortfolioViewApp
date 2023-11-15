from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Portefeuille(models.Model):
    token = models.CharField(max_length=20)
    amount=models.FloatField(null=True)
    type_actif = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    value = models.FloatField(null=True)
    unit_price = models.FloatField(null=True)
    last_update = models.DateField()
    # owner = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.token

    class Meta:
        ordering: ['type_actif', 'token', '-value']
