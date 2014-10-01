from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from easy_donor.models import Charity


def index(request):
    charity_list = Charity.objects.all()
    context = {'charity_list': charity_list}
    return render(request, 'easy_donor/index.html', context)

def donate(request):
    return HttpResponse("Please sign up")

def charity(request, charity_id):
    charity = get_object_or_404(Charity, pk=charity_id)
    return render(request, 'easy_donor/charity.html', {'charity': charity})

def sign_up(request):
    return render(request, 'easy_donor/sign_up.html')
