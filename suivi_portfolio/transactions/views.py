from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction_history, Type_actif, Type_transac, Token
from django.contrib import messages
from userpreferences.models import UserPreference
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse
import os
import json
from django.conf import settings
from portefeuille.models import Portefeuille

# Create your views here.


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        transaction = Transaction_history.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Transaction_history.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Transaction_history.objects.filter(
            date__istartswith=search_str, owner=request.user) | Transaction_history.objects.filter(
            description__icontains=search_str, owner=request.user) | Transaction_history.objects.filter(
            type_actif__icontains=search_str, owner=request.user)
        data = transaction.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    # type_actifs = Type_actif.objects.all()
    transactions = Transaction_history.objects.filter(owner=request.user)
    paginator = Paginator(transactions, 15)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'transactions': transactions,
        'page_obj': page_obj,
        'currency': currency
    }

    if request.method == 'POST':
        print("HEEERE")
        records = Transaction_history.objects.all()
        records.delete()
        return render(request, 'transaction/index.html', context)

    return render(request, 'transaction/index.html', context)


@login_required(login_url='/authentication/login')
def choose_type_transaction(request):
    type_transacs = Type_transac.objects.all()
    context = {
        'type_transacs': type_transacs
    }
    if request.method == 'GET':
        return render(request, 'transaction/choose_type_transaction.html', context)

    if request.method == 'POST':
        type_transac = request.POST['type_transac']

        messages.success(request, 'Transaction saved successfully')

        return redirect(reverse('add-transaction', kwargs={'type_transac': type_transac}))


@login_required(login_url='/authentication/login')
def add_transaction(request, type_transac):
    print("type_transac", type_transac)
    transac_form = list()
    file_path = os.path.join(settings.BASE_DIR, 'type_transaction_form.json')
    type_actifs = Type_actif.objects.all()
    # type_transacs = Type_transac.objects.all()

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            if k == type_transac:
                for k1, v1 in v.items():
                    transac_form.append(v1)

    context = {
        'type_actifs': type_actifs,
        'type_transacs': type_transac,
        'form_data': transac_form,
        'values': request.POST,
        'standard_form': ['text', 'number', 'date']

    }
    print(context['form_data'])
    if request.method == 'GET':
        return render(request, 'transaction/add_transaction.html', context)

    if request.method == 'POST':
        amount1 = request.POST['amount1']

        if not amount1:
            messages.error(request, 'Amount is required')
            return render(request, 'transaction/add_transaction.html', context)
        print(request.POST)
        token1 = request.POST['token1']
        type_actif1 = request.POST['type_actif_token1']
        descriptif1 = request.POST['descriptif1']
        date = request.POST['transaction_date']
        unit_price1 = request.POST['unit_price1']
        value1 = request.POST['value1']
        if type_transac == "Swap":
            token2 = request.POST['token2']
            type_actif2 = request.POST['type_actif_token2']
            descriptif2 = request.POST['descriptif2']
            amount2 = request.POST['amount2']
            unit_price2 = request.POST['unit_price2']
            value2 = request.POST['value2']
        else:
            token2 = None
            type_actif2 = None
            descriptif2 = None
            amount2 = 0.0
            unit_price2 = 0.0
            value2 = 0.0

        if date == "":
            date = now()

        if not descriptif1:
            messages.error(request, 'description is required')
            return render(request, 'transaction/add_transaction.html', context)

        Transaction_history.objects.create(owner=request.user, amount1=amount1, amount2=amount2, date=date,
                                           type_actif1=type_actif1, description1=descriptif1,
                                           token1=token1, type_actif2=type_actif2, description2=descriptif2,
                                           token2=token2, type_transaction=type_transac, unit_price1=unit_price1,
                                           value1=value1, unit_price2=unit_price2, value2=value2)
        update_portefeuille(request.POST, type_transac)
        if not Token.objects.filter(symbole=token1).exists():
            Token.objects.create(name=descriptif1, symbole=token1)
        if (not Token.objects.filter(symbole=token2).exists()) and token2:
            Token.objects.create(name=descriptif2, symbole=token2)
        messages.success(request, 'Transaction saved successfully')

        return redirect('transactions')


def update_portefeuille(request_post, type_transaction):
    if not Portefeuille.objects.filter(token=request_post['token1']):
        Portefeuille.objects.create(token=request_post['token1'],
                                    amount=request_post['amount1'],
                                    unit_price=float(
                                        request_post['unit_price1']),
                                    value=float(request_post['value1']),
                                    type_actif=request_post['type_actif_token1'],
                                    description=request_post['descriptif1'],
                                    last_update=now()
                                    )
    else:
        token_1 = Portefeuille.objects.get(token=request_post['token1'])
        print("here", token_1.amount, request_post['amount1'])
        token_1.amount += float(request_post['amount1'])
        token_1.unit_price = float(request_post['unit_price1'])
        token_1.last_update = now()
        token_1.save()

    if type_transaction == "Swap":
        if not Portefeuille.objects.filter(token=request_post['token2']):
            Portefeuille.objects.create(token=request_post['token2'],
                                        amount=request_post['amount2'],
                                        unit_price=float(
                                            request_post['unit_price2']),
                                        value=float(request_post['value2']),
                                        type_actif=request_post['type_actif_token2'],
                                        description=request_post['descriptif2'],
                                        last_update=now())
        else:
            token_2 = Portefeuille.objects.get(token=request_post['token2'])
            token_2.amount += float(request_post['amount2'])
            token_2.unit_price = float(request_post['unit_price1'])
            token_2.last_update = now()
            token_2.save()


@login_required(login_url='/authentication/login')
def transaction_edit(request, id):
    transaction = Transaction_history.objects.get(pk=id)
    old_amount1 = transaction.amount1
    old_amount2 = transaction.amount2
    type_actifs = Type_actif.objects.all()
    context = {
        'transaction': transaction,
        'values': transaction,
        'type_actifs': type_actifs
    }
    if request.method == 'GET':
        return render(request, 'transaction/edit_transaction.html', context)
    if request.method == 'POST':
        amount1 = request.POST['amount1']

        if not amount1:
            messages.error(request, 'Amount is required')
            return render(request, 'transaction/edit_transaction.html', context)
        token1 = request.POST['token1']
        type_actif1 = request.POST['type_actif1']
        descriptif1 = request.POST['description1']
        token2 = request.POST['token2']
        type_actif2 = request.POST['type_actif2']
        descriptif2 = request.POST['description2']
        date = request.POST['transaction_date']
        amount2 = request.POST['amount2']

        if not descriptif1:
            messages.error(request, 'description is required')
            return render(request, 'transaction/edit_transaction.html', context)

        transaction.owner = request.user
        transaction.token1 = token1
        transaction.amount1 = amount1
        transaction.date = date
        transaction.type_actif1 = type_actif1
        transaction.description1 = descriptif1
        transaction.token2 = token2
        transaction.amount2 = amount2
        transaction.type_actif2 = type_actif2
        transaction.description2 = descriptif2

        transaction.save()
        request_post = request.POST.copy()
        request_post['amount1'] = float(amount1) - float(old_amount1)

        if request.POST['token2']:
            request_post['amount2'] = float(amount2) - float(old_amount2)
        print("type_transaction", transaction.type_transaction)
        update_portefeuille(request_post, transaction.type_transaction)
        messages.success(request, 'transaction updated  successfully')

        return redirect('transactions')


def transaction_delete(request, id):
    transaction = Transaction_history.objects.get(pk=id)
    token_1 = transaction.token1
    token_2 = transaction.token2
    old_amount1 = transaction.amount1
    old_amount2 = transaction.amount2
    type_trans = transaction.type_transaction
    transaction.delete()
    request_post = {
        'token1': token_1,
        'token2': token_2,
        'amount1': -old_amount1,
        'amount2': -old_amount2,
    }
    update_portefeuille(request_post, type_trans)
    messages.success(request, 'Transaction removed')
    return redirect('transactions')
