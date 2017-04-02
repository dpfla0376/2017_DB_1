# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbApp', '0004_auto_20170328_0228'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rack',
            old_name='asset',
            new_name='assetInfo',
        ),
        migrations.RenameField(
            model_name='server',
            old_name='asset',
            new_name='assetInfo',
        ),
        migrations.RenameField(
            model_name='storageasset',
            old_name='asset',
            new_name='assetInfo',
        ),
        migrations.RenameField(
            model_name='switch',
            old_name='asset',
            new_name='assetInfo',
        ),
        migrations.AlterField(
            model_name='userservice',
            name='grant',
            field=models.IntegerField(max_length=45),
            preserve_default=True,
        ),
    ]
