# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('easy_donor', '0002_donation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charity',
            name='phone',
            field=models.CharField(max_length=12),
        ),
    ]
