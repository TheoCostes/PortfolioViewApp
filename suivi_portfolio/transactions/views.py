from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='/authentication/login')
def index(request):
    return render(request, 'transaction/index.html')


def add_transaction(request):
    return render(request, 'transaction/add_transaction.html')
