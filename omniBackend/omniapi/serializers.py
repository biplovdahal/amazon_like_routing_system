from django.contrib.auth.models import User, Group
from rest_framework import serializers
from omniBackend.omniapi.models import Route, Order, Location, Van


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url','username','email','groups')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url','name')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('address','city')

class VanSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Van
        fields = ('__all__')



class RouteSerializer(serializers.ModelSerializer):
    van = VanSerailizer()
    class Meta:
        model = Route
        fields = ('__all__')
    def create(self, validated_data):
        miles_from_warehouse = validated_data['miles_from_warehouse']
        driver_first_name = dict(validated_data['van'])['driver_first_name']
        van = Van(driver_first_name=driver_first_name)
        van.save()
        route = Route(miles_from_warehouse=miles_from_warehouse,van=van)
        route.save()
        return route


class OrderSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    class Meta:
        model = Order
        fields=('id','location','timestamp','route','order_cost')
        extra_kwargs = {
            'timestamp':{
                'read_only':False,
                'required':True
            },
            'route':{
                'read_only':True,
            }
            'order_cost':{
                'read_only':True,
            }

        }
