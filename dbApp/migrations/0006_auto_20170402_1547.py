# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-02 06:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbApp', '0005_auto_20170402_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storage',
            name='diskSpec',
            field=models.CharField(max_length=45),
        ),
    ]