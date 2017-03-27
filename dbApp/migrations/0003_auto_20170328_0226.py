# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbApp', '0002_auto_20170328_0224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverlocation',
            name='rack_pk',
            field=models.ForeignKey(to='dbApp.Rack', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='switch',
            name='IP',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
