from django.db import models

class Donor(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    phone = models.IntegerField(max_length=12)
    balanced_href = models.CharField(max_length=200)
    funding_instrument = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Charity(models.Model):
    business_name = models.CharField(max_length=200)
    ein = models.IntegerField(max_length=9)
    email = models.EmailField(max_length=254)
    phone = models.IntegerField(max_length=12)
    balanced_href = models.CharField(max_length=200)
    funding_instrument = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True)
    url = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.business_name


class Order(models.Model):
    donor = models.ForeignKey(Donor)
    charity = models.ForeignKey(Charity)
    amount = models.IntegerField(default=0)
    balanced_href = models.CharField(max_length=200)

    def __str__(self):
        return self.balanced_href
