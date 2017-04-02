# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-02 07:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dbApp', '0006_auto_20170402_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverlocation',
            name='server_pk',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dbApp.Server'),
        ),
        migrations.AlterField(
            model_name='switchlocation',
            name='switch',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='dbApp.Switch'),
        ),
    ]
