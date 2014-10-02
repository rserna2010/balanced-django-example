from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django import forms
from django.forms import ModelForm
from django.conf import settings

from easy_donor.models import Charity

import balanced
balanced.configure(settings.BALANCED['secret'])


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
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CharityForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            new_charity = form.save()

            # Create a Balanced Customer
            customer = balanced.Customer(
                business_name=new_charity.business_name,
                ein=new_charity.ein,
                email=new_charity.email,
                phone=new_charity.phone
            ).save()

            # Store Balanced Customer Href to database
            new_charity.balanced_href = customer.href
            new_charity.save()

            # redirect to a new URL:
            return HttpResponseRedirect('/easy_donor/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CharityForm()
    return render(request, 'easy_donor/sign_up.html', {'form': form})


class CharityForm(ModelForm):
    class Meta:
        model = Charity
        fields = ['business_name', 'ein', 'email', 'phone', 'description',
                  'url']
