# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-02 05:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbApp', '0006_auto_20170402_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='assetNum',
            field=models.CharField(db_index=True, max_length=45),
        ),
    ]
