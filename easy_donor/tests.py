from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from easy_donor.models import Charity, Donation

import balanced
import sys

# https://www.balancedpayments.com/docs/testing
FIXTURES = {
    'card': {
        'number': 4111111111111111,
        'expiration_month': 12,
        'expiration_year': 2020,
        'name': 'Heisenberg'
    },
    'bank_account': {
        'account_number': 9900000001,
        'routing_number': 121000358,
        'account_type': 'checking',
        'name': 'Walter White',
    },
    'charity': {
        'business_name': 'Salvation Army',
        'ein': '123456789',
        'email': 'sal@salvationarmy.com',
        'phone':'7131234567',
        'description': 'An international charitable organization.',
        'url': 'http://www.salvationarmyusa.org'
    }
}


def create_charity():
    charity = Charity(business_name="Salvation Army",
                      ein='123456789',
                      email='sal@salvationarmy.com',
                      phone='7131234567',
                      description="An international charitable organization.",
                      url='http://www.salvationarmyusa.org'
    )
    charity.save()
    return charity


def create_bank_account():
    bank_account = balanced.BankAccount(**FIXTURES['bank_account']).save()
    return bank_account


class ModelsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        balanced.configure(settings.BALANCED['secret'])

        card = balanced.Card(**FIXTURES['card']).save()
        # add some money to the escrow account
        card.debit(amount=100000)

        bank_account = balanced.BankAccount(**FIXTURES['bank_account']).save()
        cls.charity = Charity(business_name="Salvation Army",
                              ein='123456789',
                              email='sal@salvationarmy.com',
                              phone='7131234567',
                              balanced_href=bank_account.href,
                              funding_instrument=bank_account.href,
                              description="An international charitable organization.",
                              url='http://www.salvationarmyusa.org')
        cls.charity.save()

    def setUp(self):
        pass

    def test_create_credit(self):
        bank_account = balanced.BankAccount(**FIXTURES['bank_account'])
        bank_account.save()
        credit = bank_account.credit(amount=1000)
        self.assertEqual(credit.amount, 1000)

    def test_create_bank_account(self):
        bank_account = balanced.BankAccount(**FIXTURES['bank_account'])
        bank_account.save()
        self.assertTrue(bank_account.href)


class CharityModelTests(TestCase):
    def test_ein_not_string(self):

        charity = Charity(business_name="Salvation Army",
                          ein='adsfsadf',
                          email='sal@salvationarmy.com',
                          phone='7131234567',
                          balanced_href="/customers/CU4uivujjTtUiWznmWBizVba",
                          funding_instrument="/cards/CC6E5YUgwWa9IoKyKPyFW0rw",
                          description="An international charitable organization.",
                          url='http://www.salvationarmyusa.org')
        with self.assertRaises(ValueError):
            charity.save()


class CharityViewTests(TestCase):
    def test_index_view_with_no_charities(self):
        response = self.client.get(reverse('easy_donor:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Easy")
        self.assertQuerysetEqual(response.context['charity_list'], [])

    def test_index_view_with_no_charities(self):
        create_charity()
        response = self.client.get(reverse('easy_donor:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Salvation Army")
        self.assertQuerysetEqual(response.context['charity_list'],
                                 ['<Charity: Salvation Army>'])


class CharityFormTests(TestCase):
    def test_create_charity_form(self):
        response = self.client.post(reverse('easy_donor:sign_up'),
                                    {'business_name': 'Salvation Army',
                                     'ein': '123456789',
                                     'email': 'sal@salvationarmy.com',
                                     'phone':'7131234567',
                                     'description': 'An international '
                                                    'charitable organization.',
                                     'url': 'http://www.salvationarmyusa.org'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['charity_id'], 2)

    def test_charity_form_with_short_ein(self):
        response = self.client.post(reverse('easy_donor:sign_up'),
                                    {'business_name': 'Salvation Army',
                                     'ein': '12345678',
                                     'email': 'sal@salvationarmy.com',
                                     'phone': '7131234567',
                                     'description': 'An international '
                                                    'charitable organization.',
                                     'url': 'http://www.salvationarmyusa.org'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ensure this value has at least 9 characters")

    def test_charity_form_with_noninteger_ein(self):
        response = self.client.post(reverse('easy_donor:sign_up'),
                                        {'business_name': 'Salvation Army',
                                         'ein': '12345678A',
                                         'email': 'sal@salvationarmy.com',
                                         'phone': '7131234567',
                                         'description': 'An international '
                                                        'charitable organization.',
                                         'url': 'http://www.salvationarmyusa.org'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "value must be an integer")

    def test_charity_form_with_invalid_phone_number(self):
        response = self.client.post(reverse('easy_donor:sign_up'),
                                        {'business_name': 'Salvation Army',
                                         'ein': '123456789',
                                         'email': 'sal@salvationarmy.com',
                                         'phone': '123b',
                                         'description': 'An international '
                                                        'charitable organization.',
                                         'url': 'http://www.salvationarmyusa.org'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phone number must be entered in the"
                                      " format")

    def test_charity_form_with_invalid_phone_number(self):
        response = self.client.post(reverse('easy_donor:sign_up'),
                                    {'business_name': 'Salvation Army',
                                     'ein': '123456789',
                                     'email': 'sal@salvationarmy.com',
                                     'phone': '7131234567',
                                     'description': 'An international '
                                                    'charitable organization.',
                                     'url': 'salvationarmyusa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a valid URL")

    def test_charity_add_funding_instrument(self):
        charity = create_charity()
        bank_account = balanced.BankAccount(**FIXTURES['bank_account']).save()
        response = self.client.post(
            reverse('easy_donor:add_funding_instrument'),
            {
                'href':  bank_account.href,
                'charity_id': charity.id
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "finished")


class DonateViewsTests(TestCase):
    def test_create_donation(self):
        create_charity_response = self.client.post(reverse('easy_donor:sign_up'),
                                    {'business_name': 'Salvation Army',
                                     'ein': '123456789',
                                     'email': 'sal@salvationarmy.com',
                                     'phone':'7131234567',
                                     'description': 'An international '
                                                    'charitable organization.',
                                     'url': 'http://www.salvationarmyusa.org'})

        bank_account = balanced.BankAccount(**FIXTURES['bank_account']).save()
        create_bank_account_response = self.client.post(
            reverse('easy_donor:add_funding_instrument'),
            {
                'href':  bank_account.href,
                'charity_id': create_charity_response.context['charity_id']
            }
        )

        card = balanced.Card(**FIXTURES['card']).save()
        response = self.client.post(
            reverse('easy_donor:donate'),
            {
                'href':  card.href,
                'amount':  5,
                'charity_id': create_charity_response.context['charity_id']
            }
        )
        self.assertEqual(response.status_code, 200)
        donation = Donation.objects.get(pk=1)
        self.assertEqual(donation.amount, 500)
        self.assertRegexpMatches(donation.balanced_order_href, '/orders/')

        # confirm Balanced order amounts
        order = balanced.Order.fetch(donation.balanced_order_href)
        self.assertEqual(order.amount, 500)
        self.assertEqual(order.description, 'Salvation Army')
        self.assertEqual(order.amount_escrowed, 0)
        charity = Charity.objects.get(
            pk=create_charity_response.context['charity_id'])
        self.assertEqual(order.merchant.href, charity.balanced_href)


    def test_create_donation_with_decimal_amount(self):
        create_charity_response = self.client.post(reverse('easy_donor:sign_up'),
                                                   {'business_name': 'Salvation Army',
                                                    'ein': '123456789',
                                                    'email': 'sal@salvationarmy.com',
                                                    'phone':'7131234567',
                                                    'description': 'An international '
                                                                   'charitable organization.',
                                                    'url': 'http://www.salvationarmyusa.org'})

        bank_account = balanced.BankAccount(**FIXTURES['bank_account']).save()
        create_bank_account_response = self.client.post(
            reverse('easy_donor:add_funding_instrument'),
            {
                'href':  bank_account.href,
                'charity_id': create_charity_response.context['charity_id']
            }
        )

        card = balanced.Card(**FIXTURES['card']).save()
        response = self.client.post(
            reverse('easy_donor:donate'),
            {
                'href':  card.href,
                'amount':  5.00,
                'charity_id': create_charity_response.context['charity_id']
            }
        )
        self.assertEqual(response.status_code, 200)
        donation = Donation.objects.get(pk=2)
        self.assertEqual(donation.amount, 500)
        self.assertRegexpMatches(donation.balanced_order_href, '/orders/')


