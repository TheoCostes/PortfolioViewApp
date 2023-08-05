from django.shortcuts import render
from .models import Portefeuille
from transactions.models import Token
from django.contrib import messages
from userpreferences.models import UserPreference
from django.utils.timezone import now
from django.core.paginator import Paginator
from .utils_api import get_prices
# Create your views here.

def index(request):
    get_prices(Portefeuille)
    portefeuille = Portefeuille.objects.all()
    
    paginator = Paginator(portefeuille, 50)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'protefeuille': portefeuille,
        'page_obj': page_obj,
        'currency': currency,
    }
    print(context)

    if request.method == 'POST':
        records = Portefeuille.objects.all()
        for el in records:
            if not(Token.objects.filter(symbole=el.token).exists()):
                print
                el.delete()
            else:
                print(el)
                el.amount=0.0
                el.save()
                print(el)
                print('----')
        return render(request, 'portefeuille/index.html', context)
    return render(request, 'portefeuille/index.html', context)
