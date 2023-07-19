from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'transaction/index.html')


def add_transaction(request):
    return render(request, 'transaction/add_transaction.html')
