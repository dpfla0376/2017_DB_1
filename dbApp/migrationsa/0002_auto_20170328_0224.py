# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='IP',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
