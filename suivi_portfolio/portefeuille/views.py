from django.shortcuts import render
from .models import Portefeuille
from django.contrib import messages
from userpreferences.models import UserPreference
from django.utils.timezone import now
from django.core.paginator import Paginator
# Create your views here.

def index(request):
    portefeuille = Portefeuille.objects.all()
    paginator = Paginator(portefeuille, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    print(portefeuille.count)
    context = {
        'protefeuille': portefeuille,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'portefeuille/index.html', context)
