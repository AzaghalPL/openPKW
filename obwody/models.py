from django.db import models
from django.contrib.contenttypes.models import *
from django.contrib.contenttypes.fields import *

# Create your models here.

class Obwod(models.Model):
	name = models.CharField(max_length=255)
	version = models.IntegerField(default=0)
	cards = models.PositiveIntegerField(default=0)
	population = models.PositiveIntegerField(default=0)
	in_city_status = models.BooleanField(default=0)
	def in_city(self):
		return bool(self.in_city_status)
	area_type = models.ForeignKey(ContentType)
	area_id = models.PositiveIntegerField()
	area = GenericForeignKey("area_type", "area_id")
	class Meta:
		index_together = ["in_city_status", "area_id"]

class Wojewodztwo(models.Model):
	name = models.CharField(max_length=50)

class Powiat(models.Model):
	name = models.CharField(max_length=50)
	wojewodztwo = models.ForeignKey(Wojewodztwo)
	city_status = models.BooleanField(default=0)
	def city(self):
		return bool(self.city_status)
	obwody = GenericRelation(Obwod, related_query_name='parent', content_type_field='area_type', object_id_field='area_id');

class Gmina(models.Model):
	name = models.CharField(max_length=50)
	powiat = models.ForeignKey(Powiat)
	obwody = GenericRelation(Obwod, related_query_name='parent', content_type_field='area_type', object_id_field='area_id');
