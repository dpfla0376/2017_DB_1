from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
"""
class User(models.Model):
    user_pk = models.IntegerField()
	userID = models.CharField(max_length=45)
    name = models.CharField(max_length=45)
    email = models.CharField(max_length=45)
	password = models.CharField(max_length=45)
"""
	
class Service(models.Model):
	serviceName = models.CharField(max_length=45)
	makeDate = models.DateField()
	color = models.IntegerField()
	
class Asset(models.Model):
	assetNum = models.CharField(max_length=45,db_index=True)
	acquisitionDate = models.DateField(auto_now_add = True)
	assetName = models.CharField(max_length=45)
	standard = models.CharField(max_length=45)
	acquisitionCost = models.IntegerField()
	purchaseLocation = models.CharField(max_length=45)
	maintenanceYear = models.IntegerField()

class StorageAsset(models.Model):
	manageNum =models.CharField(max_length=45)
	assetInfo = models.ForeignKey(Asset)
	manageSpec =models.CharField(max_length=45)
	location = models.CharField(max_length=45)
	storageForm = models.CharField(max_length=45)
	
class Server(models.Model):
	manageNum =models.CharField(max_length=45)
	assetInfo = models.ForeignKey(Asset)
	manageSpec = models.CharField(max_length=45)
	isInRack = models.BooleanField(default=1)
	size = models.IntegerField()
	core = models.IntegerField()
	IP = models.IntegerField(null=True)

class Switch(models.Model):
	manageNum = models.CharField(max_length=45)
	assetInfo = models.ForeignKey(Asset)
	manageSpec = models.CharField(max_length=45)
	isInRack = models.BooleanField(default=1)
	size = models.IntegerField()
	IP = models.IntegerField(null=True)
	serviceOn = models.BooleanField(default=1)
	
class Rack(models.Model):
	manageNum = models.CharField(max_length=45)
	assetInfo = models.ForeignKey(Asset)
	manageSpec = models.CharField(max_length=45)
	size = models.IntegerField()
	location = models.CharField(max_length=45)

class Storage(models.Model):
	storageAsset = models.ForeignKey(StorageAsset)
	enrollDate = models.DateField()
	diskSpec = models.FloatField()
	allocUnitSize = models.FloatField()
	Vol = models.FloatField()
	
class ServerService(models.Model):
	server = models.ForeignKey(Server)
	service = models.ForeignKey(Service)
	alloclDate = models.DateField(auto_now_add = True)
	Use	= models.BooleanField(default=1)

class ServerLocation(models.Model):
	server_pk = models.ForeignKey(Server)
	rack_pk = models.ForeignKey(Rack,null=True)
	rackLocation = models.IntegerField(null=True)
	realLocation =  models.CharField(max_length=45,null=True)
	
class SwitchLocation(models.Model):
	switch = models.ForeignKey(Switch)
	rack = models.ForeignKey(Rack,null=True)
	rackLocation = models.IntegerField(null=True)
	realLocation =  models.CharField(max_length=45,null=True)

class StorageService(models.Model):
	storage = models.ForeignKey(Storage)
	service = models.ForeignKey(Service)
	allocSize = models.FloatField()
	usage =  models.CharField(max_length=45)
	
class UserService(models.Model):
	user = models.ForeignKey(User)
	service = models.ForeignKey(Service)
	grant =  models.IntegerField()
	serviceName =  models.CharField(max_length=45)

	



		