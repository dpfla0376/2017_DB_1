# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assetName', models.CharField(max_length=45)),
                ('acquisitionDate', models.DateField(auto_now_add=True)),
                ('assetNum', models.CharField(max_length=45)),
                ('purchaseLocation', models.CharField(max_length=45)),
                ('maintenanceYear', models.IntegerField()),
                ('standard', models.CharField(max_length=45)),
                ('acquisitionCost', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('manageNum', models.CharField(max_length=45)),
                ('manageSpec', models.CharField(max_length=45)),
                ('size', models.IntegerField()),
                ('location', models.CharField(max_length=45)),
                ('asset', models.ForeignKey(to='dbApp.Asset')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('manageNum', models.CharField(max_length=45)),
                ('manageSpec', models.CharField(max_length=45)),
                ('isInRack', models.BooleanField(default=1)),
                ('size', models.IntegerField()),
                ('location', models.CharField(max_length=45)),
                ('core', models.IntegerField()),
                ('IP', models.IntegerField()),
                ('serviceOn', models.BooleanField(default=1)),
                ('asset', models.ForeignKey(to='dbApp.Asset')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServerLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rackLocation', models.IntegerField()),
                ('realLocation', models.CharField(max_length=45)),
                ('rack_pk', models.ForeignKey(to='dbApp.Rack')),
                ('server_pk', models.ForeignKey(to='dbApp.Server')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServerService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alloclDate', models.DateField(auto_now_add=True)),
                ('Use', models.BooleanField(default=1)),
                ('server', models.ForeignKey(to='dbApp.Server')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serviceName', models.CharField(max_length=45)),
                ('makeDate', models.DateField()),
                ('color', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enrollDate', models.DateField()),
                ('diskSpec', models.FloatField()),
                ('allocUnitSize', models.FloatField()),
                ('Vol', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StorageAsset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('manageNum', models.CharField(max_length=45)),
                ('manageSpec', models.CharField(max_length=45)),
                ('location', models.CharField(max_length=45)),
                ('storageForm', models.IntegerField()),
                ('asset', models.ForeignKey(to='dbApp.Asset')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StorageService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allocSize', models.FloatField()),
                ('usage', models.CharField(max_length=45)),
                ('service', models.ForeignKey(to='dbApp.Service')),
                ('storage', models.ForeignKey(to='dbApp.Storage')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Switch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('manageNum', models.CharField(max_length=45)),
                ('manageSpec', models.CharField(max_length=45)),
                ('isInRack', models.BooleanField(default=1)),
                ('size', models.IntegerField()),
                ('IP', models.IntegerField()),
                ('serviceOn', models.BooleanField(default=1)),
                ('asset', models.ForeignKey(to='dbApp.Asset')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SwitchLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rackLocation', models.IntegerField()),
                ('realLocation', models.CharField(max_length=45)),
                ('rack', models.ForeignKey(to='dbApp.Rack')),
                ('switch', models.ForeignKey(to='dbApp.Switch')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('color', models.CharField(max_length=45)),
                ('serviceName', models.CharField(max_length=45)),
                ('service', models.ForeignKey(to='dbApp.Service')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='storage',
            name='storageAsset',
            field=models.ForeignKey(to='dbApp.StorageAsset'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='serverservice',
            name='service',
            field=models.ForeignKey(to='dbApp.Service'),
            preserve_default=True,
        ),
    ]
