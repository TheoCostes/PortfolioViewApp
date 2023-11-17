import sys
sys.path.insert(0, "..")

from django.shortcuts import render
from portefeuille.models import Portefeuille
from transactions.models import Token
from django.contrib import messages
from userpreferences.models import UserPreference
from django.utils.timezone import now
from django.core.paginator import Paginator
from .utils_api import get_prices
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='/authentication/login')
def index(request):
    get_prices(Portefeuille)
    portefeuille = Portefeuille.objects.all()
    actifs = {}
    total = 0
    for objet in portefeuille:
        groupe = objet.type_actif
        if groupe in actifs:
            actifs[groupe]["object"].append(objet)
            actifs[groupe]["somme"]+= objet.value
            total += objet.value
        else:
            actifs[groupe] = {"object" : [objet],
                              "somme" : objet.value                              
            }
            total += objet.value
    # paginator = Paginator(portefeuille, 50)
    # page_number = request.GET.get('page')
    # page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'actifs': actifs,
        # 'page_obj': page_obj,
        'currency': currency,
        'total':total
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
