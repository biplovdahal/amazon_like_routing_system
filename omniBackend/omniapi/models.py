from __future__ import unicode_literals
from django.db import models


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    latitude = models.CharField(max_length=120,default=None, blank=True, null=True)
    longitude = models.CharField(max_length=120,default=None, blank=True, null=True)
    city = models.CharField(max_length=120,default=None, blank=True, null=True)
    state = models.CharField(max_length=120,default=None, blank=True, null=True)
    country = models.CharField(max_length=120,default=None, blank=True, null=True)
    address = models.CharField(max_length=120,default=None, blank=True, null=True)
    zipcode = models.CharField(max_length=120,default=None, blank=True, null=True)
    def __repr__ (self):
        return '<Location %s>' % self.city
    def __str__ (self):
        return self.city


class Van(models.Model):
    id = models.AutoField(primary_key=True)
    driver_first_name = models.CharField(max_length=120,blank=True, null=True)
    driver_last_name = models.CharField(max_length=120,blank=True,null=True)
    van_car_plate = models.CharField(max_length=120, blank=True, null=True, unique=True)
    def __repr__ (self):
        return '<Van %s>' % self.driver_first_name
    def __str__ (self):
        return self.driver_first_name


class Route(models.Model):
    id = models.AutoField(primary_key=True)
    van = models.ForeignKey(Van, on_delete=models.PROTECT)
    miles_from_warehouse = models.IntegerField(null=True)
    cost = models.CharField(max_length=120, blank=True, null=True)
    def __repr__ (self):
        return '<Route {0} miles ${1}>'.format(self.miles_from_warehouse, self.cost)
    def __str__ (self):
        return str(self.id)


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    order_type = models.CharField(max_length=120,default=None, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(blank=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    order_cost =  models.IntegerField(null=True)
    def __repr__ (self):
        return '<Order Type: {0} Route:{1} City:{2}>'.format(self.order_type, self.route, self.location.city)
