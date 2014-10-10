from django.test import TestCase
from django.core.urlresolvers import reverse



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
        'routing_number': 121000358,  # SMCU
        'account_type': 'checking',
        'name': 'Walter White',
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
        cls.api_key = balanced.APIKey().save()
        balanced.configure(cls.api_key.secret)
        cls.marketplace = balanced.Marketplace().save()
        card = balanced.Card(**FIXTURES['card']).save()

        # add some money to the escrow account
        card.debit(amount=100000)

        bank_account = balanced.BankAccount(**FIXTURES['bank_account']).save()
        cls.charity = Charity(business_name="Salvation Army",
                              ein='123456789',
                              email='sal@salvationarmy.com',
                              phone='7131234567',
                              balanced_href=bank_account.href,
                              funding_instrument="/cards/CC6E5YUgwWa9IoKyKPyFW0rw",
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
    @classmethod
    def setUpClass(cls):
        cls.api_key = balanced.APIKey().save()
        balanced.configure(cls.api_key.secret)
        cls.marketplace = balanced.Marketplace().save()
        card = balanced.Card(**FIXTURES['card']).save()

        # add some money to the escrow account
        card.debit(amount=100000)

    def setUp(self):
        pass

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

    def test_charity_page_returns_appropriate_info(self):
        charity = create_charity()
        response = self.client.get(reverse('easy_donor:charity', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, charity.name)
        self.assertContains(response, charity.url)
        self.assertContains(response, charity.description)
