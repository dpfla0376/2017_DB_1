# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbApp', '0003_auto_20170328_0226'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userservice',
            name='color',
        ),
        migrations.AddField(
            model_name='userservice',
            name='grant',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='serverlocation',
            name='rackLocation',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serverlocation',
            name='realLocation',
            field=models.CharField(max_length=45, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='switchlocation',
            name='rack',
            field=models.ForeignKey(to='dbApp.Rack', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='switchlocation',
            name='rackLocation',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='switchlocation',
            name='realLocation',
            field=models.CharField(max_length=45, null=True),
            preserve_default=True,
        ),
    ]
