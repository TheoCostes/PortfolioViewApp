from django.db import models

# Create your models here.

class Historique(models.Model):
    save_date = models.DateField()
    token = models.CharField(max_length=20)
    amount=models.FloatField(null=True)
    type_actif = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    value = models.FloatField(null=True)
    unit_price = models.FloatField(null=True)
    # last_update = models.DateField()
    
    def __str__(self) -> str:
        return f"{str(self.save_date)} - {self.token}"

    class Meta:
        ordering: ['-save-date','type_actif', 'token', '-value']