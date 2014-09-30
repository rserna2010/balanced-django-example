from django.db import models

class Donor(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField([max_length=254, **options])
    created_at = models.DateTimeField('date published')

class Charity(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

class Order(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
