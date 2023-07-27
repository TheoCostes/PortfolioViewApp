from django.db import models
from django.utils.timezone import now

from django.contrib.auth.models import User
# Create your models here.

class Transaction_history(models.Model):
    type_transaction = models.CharField(max_length=100, default="Swap")
    amount1=models.FloatField()
    type_actif1 = models.CharField(max_length=100)
    token1 = models.CharField(max_length=20)
    description1 = models.CharField(max_length=150)
    amount2=models.FloatField(default=0.0, null=True,blank=True)
    type_actif2 = models.CharField(max_length=100, null=True,blank=True)
    token2 = models.CharField(max_length=20, null=True,blank=True)
    description2 = models.CharField(max_length=150, null=True,blank=True)
    date= models.DateField(default=now)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.type_transaction+" - "+self.token1+" - "+str(self.date)

    class Meta:
        ordering: ['date']
        


class Type_actif(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Actifs'

    def __str__(self):
        return self.name


class Type_transac(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Type Transactions'

    def __str__(self):
        return self.name
    
class Token(models.Model):
    name = models.CharField(max_length=100)
    symbole = models.CharField(max_length=20)
    class Meta:
        verbose_name_plural = 'token'

    def __str__(self):
        return self.name

