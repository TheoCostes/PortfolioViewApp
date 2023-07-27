from django.contrib import admin
from .models import Token, Transaction_history, Type_actif, Type_transac
# Register your models here.

admin.site.register(Transaction_history)
admin.site.register(Type_actif)
admin.site.register(Type_transac)
admin.site.register(Token)
