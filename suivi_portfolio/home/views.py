from django.shortcuts import render
from portefeuille.models import Portefeuille
from userpreferences.models import UserPreference
from .models import Historique
from django.db.models import Sum
from django.utils.timezone import now
from datetime import datetime
# Create your views here.

def index(request):
    populate_models_historique(Portefeuille)
    total = Portefeuille.objects.aggregate(Sum('value'))
    port_month = Historique.objects.filter(save_date=datetime.today().replace(day=1))
    value_month = port_month.aggregate(Sum('value'))['value__sum']
    port_year = Historique.objects.filter(save_date=datetime.today().replace(month=1,day=1))
    value_year = port_year.aggregate(Sum('value'))['value__sum']
    currency = UserPreference.objects.get(user=request.user).currency
    
    data_line = Historique.objects.values('save_date', 'type_actif').annotate(value=Sum('value'))
    print(data_line)
    data_line_dict = listDict_2_dictList(data_line)
    print(data_line_dict) 
    context = {
        "total" : total["value__sum"],
        "value_mtd" : (total["value__sum"] / value_month - 1) * 100,
        "value_ytd" : (total["value__sum"] / value_year - 1) * 100,
        "currency" : currency,
        "data_line" : data_line_dict,
    }
    print(context)
    return render(request, 'home/index.html', context)

def listDict_2_dictList(list_):
    shape_dict = list(list_[0].keys())
    
    print(shape_dict)
    resu = {k:[] for k in shape_dict}
    for d in list_:
        for k,v in d.items():
            resu[k].append(v)

    return resu


def populate_models_historique(portefeuille, date=None):
    if date==None:
        date = now()
    if not Historique.objects.filter(save_date=date).exists():
        port = portefeuille.objects.all()
        for obj in port:
            Historique.objects.create(save_date=date,
                                        token=obj.token,
                                        amount=obj.amount,
                                        unit_price=obj.unit_price,
                                        value=obj.value,
                                        type_actif=obj.type_actif,
                                        description=obj.description
                                        )
            