from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from omniBackend.omniapi.serializers import UserSerializer, GroupSerializer, OrderSerializer, RouteSerializer, VanSerailizer
from omniBackend.omniapi.models import Route, Order, Location, Van
from rest_framework.response import Response
import geopy.distance
from django.db.models import Q
import datetime
from rest_framework import status
import requests
from rest_framework.views import APIView
import numpy as np
import datetime as dt

warehouse_location = '975 Bryant St, San Francisco, CA 94103'


def get_best_possible_route(distance,timestamp):
    '''
        So; here what I do is return all the closest 10 mile radius routes; for a the given order location.
        Then; after I iterate each orders; to check if given timestamp is relevant to each order; if found; return a order if not; return None.
        This could also satsify as an util function, created as a wrapper.
        This function returns an array of dictionaries with best possible route for given timestamp.
    '''
    #actual_time = timestamp.split('T')[-1]
    backwards = int(distance.replace(',','').replace('mi','').strip())-5
    frontwards = int(distance.replace(',','').replace('mi',''))+5
    backwards = str(backwards).split('.')[0]
    frontwards = str(frontwards).split('.')[0]
    if "-" in str(backwards):
        backwards = str(distance).split('.')[0]

    # get closest future and closest past, calculate the nearest using current timestamp
    routes = Route.objects.filter(miles_from_warehouse__range=(backwards,frontwards))
    applicable_routes_arr = []
    for route in routes:
        applicable_route_items = {}
        today = datetime.datetime.today()
        applicable_route = route.order_set.filter(timestamp__gt=timestamp).order_by('timestamp').first()
        if applicable_route: ##closest future exists
            applicable_route_items['route_id'] = applicable_route.route.id
            applicable_route_items['timestamp'] = applicable_route.timestamp
            applicable_route_items['cost'] = 40 #Here we offer cheap services; since we already have cars going that route.
            applicable_routes_arr.append(applicable_route_items)

        else: ## closest past exists
            applicable_route = route.order_set.filter(timestamp__lt=timestamp).order_by('-timestamp')[0]
            applicable_route_items['route_id'] = applicable_route.route.id
            applicable_route_items['timestamp'] = applicable_route.timestamp
            applicable_route_items['cost'] = 40 #Here we offer cheap services; since we already have cars going that route.
            applicable_routes_arr.append(applicable_route_items)



    return applicable_routes_arr







class CalculateDifficulty(APIView):
    '''
        This returns calculation based on given time/location, must pass location/timestamp as an argument
    '''
    def get(self, request, format=None):
        result = {'status':'OK', 'difficulty':''}
        location = request.GET.get('location','')
        timestamp = request.GET.get('timestamp','')
        try:
            r = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins='+location+'&destinations='+warehouse_location+'&key=AIzaSyCsZ654I7wdTl5zjDuqH7diEiRCRlbvHZ8')
            miles = r.json()['rows'][0]['elements'][0]['distance']['text'].split('.')[0]
            routes = get_best_possible_route(miles,timestamp)[0]['route_id']
            if routes:
                result['difficulty'] = 0
            else:
                result['difficulty'] = 1
            return Response(result, status=status.HTTP_200_OK)
        except:
            result['status'] = 'error'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)







class VanViewSet(viewsets.ModelViewSet):
    '''
        This viewsets lets you alter with van object aka driver.
    '''
    queryset = Van.objects.all()
    serializer_class = VanSerailizer
    def destroy(self, request, pk):
        result = {'status':'OK', 'message':''}
        van = Van.objects.get(id=pk)
        get_route_obj = van.route_set.first()

        order_for_that_route = get_route_obj.order_set.first()
        timestamp = order_for_that_route.timestamp
        location = order_for_that_route.location
        r = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins='+location.address+'&destinations='+warehouse_location+'&key=AIzaSyCsZ654I7wdTl5zjDuqH7diEiRCRlbvHZ8')
        miles = r.json()['rows'][0]['elements'][0]['distance']['text'].split('.')[0]
        route = Route.objects.get(id=get_route_obj.id)
        route.delete()
        try:
            order = Order.objects.get(id=order_for_that_route.id)
            order.delete()
        except:
            pass
        van.delete()
        routes = get_best_possible_route(miles,timestamp)
        if miles >= 5: #these are constant cost for routes; aka usually set by admins; here I just follow the logic 5 miles is less cheaper than 10 miles.
            cost = 40
        if miles >= 10:
            cost = 100
        if routes:
            route = Route.objects.get(id=routes[0]['route_id'])
            order = Order(location=location,timestamp=timestamp,route=route, order_cost=routes[0]['cost'] + cost) #Here we add constant route price + order price aka here we have determined route do exists headed same direction see get_best_possible_route() function for reference..
            order.save()
            result['new_applicable_route'] = route.id
            result['message'] = 'van deleted and routes are reorgnized!'
        else: # If all our conditions fails ex: 10 miles radius/ no dates matches, then we create new route and assign it a driver aka van.
            driver = Van.objects.filter(route=None).first() # We also make sure; the van aka driver isn't already booked with a route.
            if driver:
                route = Route(van=driver, miles_from_warehouse=str(miles.replace(',','').replace('mi','').strip()).split('.')[0],cost=cost)
                route.save()
                order = Order(location=location,timestamp=timestamp,route=route,order_cost=cost + 100)
                order.save()
                result['new_applicable_route'] = route.id
                result['message'] = 'van deleted and routes are reorgnized!'
            else:
                result['message'] = 'sorry all van drivers are already booked there rebuilding routes wont work'
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)




class RouteViewSet(viewsets.ModelViewSet):
    '''
        This viewsets lets you alter with route object.
    '''
    queryset = Route.objects.all()
    serializer_class = RouteSerializer



class OrderViewSet(viewsets.ModelViewSet):
    '''
        This viewset alters order object.
    '''
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self,request):
        '''
            Make sure vans are created before you create any orders.
            The way this function works is:
             - Checks if the given location is within the range of any previous routes; aka 5-10 miles radius.
             - If there aren't any routes within the range; it creates a route - with the price based on how far the location is from the warehouse. ex: 5miles=40 10miles <= 100.
             - If there are routes within the range, it makes the order cost cheaper; by adding only $40, which would be $140 for people headed towards same route and $200 for people who are not.
             - We have 2 costs. Order Cost/ Route cost; I calculate those 2 attributes and set order_cost.

        '''
        result = {'status':'OK', 'message':'','applicable_route':''}
        timestamp = dict(request.data)['timestamp'][0]
        address = dict(request.data)['location.address'][0]
        city = dict(request.data)['location.city'][0]
        r = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins='+address+'&destinations='+warehouse_location+'&key=AIzaSyCsZ654I7wdTl5zjDuqH7diEiRCRlbvHZ8')
        miles = r.json()['rows'][0]['elements'][0]['distance']['text'].split('.')[0]
        if miles >= 5: #these are constant cost for routes; aka usually set by admins; here I just follow the logic 5 miles is less cheaper than 10 miles.
            cost = 40
        if miles >= 10:
            cost = 100



        routes = get_best_possible_route(miles,timestamp)
        location = Location(address=address,city=city)
        location.save()
        if routes:
            route = Route.objects.get(id=routes[0]['route_id'])
            order = Order(location=location,timestamp=timestamp,route=route, order_cost=routes[0]['cost'] + cost) #Here we add constant route price + order price aka here we have determined route do exists headed same direction see get_best_possible_route() function for reference..
            order.save()
            result['applicable_route'] = route.id
            result['message'] = 'order confirmed!'
        else: # If all our conditions fails ex: 10 miles radius/ no dates matches, then we create new route and assign it a driver aka van.
            driver = Van.objects.filter(route=None).first() # We also make sure; the van aka driver isn't already booked with a route.
            if driver:
                route = Route(van=driver, miles_from_warehouse=str(miles.replace(',','').replace('mi','').strip()).split('.')[0],cost=cost)
                route.save()
                order = Order(location=location,timestamp=timestamp,route=route,order_cost=cost + 100)
                order.save()
                result['applicable_route'] = route.id
                result['message'] = 'order confirmed!'
            else:
                result['message'] = 'sorry all van drivers are already booked for a route! create new van obj!'
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)
