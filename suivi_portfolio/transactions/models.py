from django.db import models
from django.utils.timezone import now

from django.contrib.auth.models import User
# Create your models here.

class Transaction(models.Model):
    amount=models.FloatField()
    type_actif = models.CharField(max_length=100)
    symbole = models.CharField(max_length=20)
    description = models.CharField(max_length=150)
    date= models.DateField(default=now)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.type_actif+"-"+self.symbole+"-"+str(self.date)

    class Meta:
        ordering: ['-date']


class Type_actif(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Actifs'

    def __str__(self):
        return self.name
