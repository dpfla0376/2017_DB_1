# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-02 02:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbApp', '0005_auto_20170328_0232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userservice',
            name='grant',
            field=models.IntegerField(),
        ),
    ]
