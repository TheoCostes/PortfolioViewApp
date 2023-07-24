from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction, Type_actif
from django.contrib import messages
from userpreferences.models import UserPreference
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.http import JsonResponse
import json

# Create your views here.


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        transaction = Transaction.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Transaction.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Transaction.objects.filter(
            date__istartswith=search_str, owner=request.user) | Transaction.objects.filter(
            description__icontains=search_str, owner=request.user) | Transaction.objects.filter(
            type_actif__icontains=search_str, owner=request.user)
        data = transaction.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    # type_actifs = Type_actif.objects.all()
    transactions = Transaction.objects.filter(owner=request.user)
    paginator = Paginator(transactions, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'transactions': transactions,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'transaction/index.html', context)

@login_required(login_url='/authentication/login')
def add_transaction(request):
    type_actifs = Type_actif.objects.all()
    context = {
        'type_actifs' : type_actifs,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'transaction/add_transaction.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'transaction/add_transaction.html', context)
        print(request.POST)
        description = request.POST['description']
        symbole = request.POST['symbole']
        date = request.POST['transaction_date']
        type_actif = request.POST['type_actif']
        if date == "":
            date = now()
        print(date)

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'transaction/add_transaction.html', context)

        Transaction.objects.create(owner=request.user, amount=amount, date=date,
                               type_actif=type_actif, description=description,
                               symbole=symbole)
        messages.success(request, 'Transaction saved successfully')

        return redirect('transactions')

@login_required(login_url='/authentication/login')
def transaction_edit(request, id):
    transaction = Transaction.objects.get(pk=id)
    type_actifs = Type_actif.objects.all()
    context = {
        'transaction': transaction,
        'values': transaction,
        'type_actifs': type_actifs
    }
    if request.method == 'GET':
        return render(request, 'transaction/edit_transaction.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'transaction/edit_transaction.html', context)
        description = request.POST['description']
        date = request.POST['transaction_date']
        type_actif = request.POST['type_actif']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'transaction/edit_transaction.html', context)

        transaction.owner = request.user
        transaction.amount = amount
        transaction. date = date
        transaction.type_actif = type_actif
        transaction.description = description

        transaction.save()
        messages.success(request, 'transaction updated  successfully')

        return redirect('transactions')


def transaction_delete(request, id):
    transaction = Transaction.objects.get(pk=id)
    transaction.delete()
    messages.success(request, 'Transaction removed')
    return redirect('transactions')
