# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-09 11:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dbApp', '0014_auto_20170409_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rack',
            name='assetInfo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rack', to='dbApp.Asset'),
        ),
        migrations.AlterField(
            model_name='server',
            name='assetInfo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='server', to='dbApp.Asset'),
        ),
        migrations.AlterField(
            model_name='storageasset',
            name='assetInfo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='storageasset', to='dbApp.Asset'),
        ),
        migrations.AlterField(
            model_name='switch',
            name='assetInfo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='switch', to='dbApp.Asset'),
        ),
    ]
