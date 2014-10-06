from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django import forms
from django.forms import ModelForm
from django.conf import settings

from easy_donor.models import Charity, Donation

import balanced
balanced.configure(settings.BALANCED['secret'])


def index(request):
    charity_list = Charity.objects.all()
    context = {'charity_list': charity_list}
    return render(request, 'easy_donor/index.html', context)


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

            context = {'charity_id': new_charity.id}
            # redirect to a new URL:
            return render(request, 'easy_donor/add_funding_instrument.html', {'charity_id': new_charity.id})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = CharityForm()
    return render(request, 'easy_donor/sign_up.html', {'form': form})

def add_funding_instrument(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        funding_instrument_href = request.POST['href']
        charity_id= request.POST['charity_id']
        charity = Charity.objects.get(pk=charity_id)
        charity.funding_instrument=funding_instrument_href
        charity.save()

        # Fetch the Balanced bank account resource, this associates the
        # token to your marketplace
        bank_account = balanced.BankAccount.fetch(funding_instrument_href)

        # Associate the bank account to the appropriate Balanced customer
        bank_account.associate_to_customer(charity.balanced_href)
        response = JsonResponse({'location': 'finished'})
        return response

    return render(request, 'easy_donor/add_funding_instrument.html')


def donate(request):
    if request.method == 'POST':
        funding_instrument_href = request.POST['href']
        amount = request.POST['amount']
        amount = float(amount) * 100
        amount = int(amount)
        charity_id = request.POST['charity_id']

        # Fetch the donors card to debit
        card = balanced.Card.fetch(funding_instrument_href)

        # Fetch the merchant, which is the charity in this example
        charity = Charity.objects.get(pk=charity_id)
        merchant = balanced.Customer.fetch(charity.balanced_href)

        # create an Order
        order = merchant.create_order(desciption=charity.business_name)

        # debit the donor for the amount of the listing
        debit = order.debit_from(
            source=card,
            amount=(amount * 100),
            appears_on_statement_as=charity.business_name,
        )

        # credit the charity for the amount of the donation
        #
        # First, fetch the onwer's bank account to credit
        bank_account = balanced.BankAccount.fetch(charity.funding_instrument)

        order.credit_to(
            destination=bank_account,
            amount=(amount),
        )

        # Store the debit and it's order to your database
        order = Donation(charity=charity_id, amount=amount,
                         balanced_order_href=order.href)
        order.save()

        response = JsonResponse({'location': 'finished'})
        return response


class CharityForm(ModelForm):
    class Meta:
        model = Charity
        fields = ['business_name', 'ein', 'email', 'phone', 'description',
                  'url']

