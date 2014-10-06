# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Charity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('business_name', models.CharField(max_length=200)),
                ('ein', models.IntegerField(max_length=9)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.IntegerField(max_length=12)),
                ('balanced_href', models.CharField(max_length=200)),
                ('funding_instrument', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200, null=True)),
                ('url', models.CharField(max_length=200, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
