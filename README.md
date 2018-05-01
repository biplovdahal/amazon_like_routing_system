I've used swagger to list my urls out

/docs (To see the list of URLS)

INSTRUCTIONS:


Clone this project

Install the dependencies: pip install -r requirements.txt

I've used Django Rest Framework; for REST API. <br/>
As for datastore; I've used postgresql. <br/>




Fill these values<br/>
export DATABASE_NAME=<db><br/>  
export DATABASE_USER=<user><br/>
export DATABASE_PASSWORD=<user><br/>

python manage.py migrate <br/>
python manage.py makemigrations <br/>
python manage.py migrate <br/>
python manage.py runserver <br/>

Visit /docs for documentation for each API endpoints/documentation. <br/>

Key objects </br>
  Route ----> This is the commute from warehouse to location.(I've done it so; if 10 or more; charge certain amount; if 10 or less; charge cheaper.)</br>
  Van ---> This is needed, this is driver for each route. So you must have van object to even create order. (Creating Van should be the first thing)</br>
  Order --> The order itself; has obj called order_cost which is the final pricing with route cost added ontop of it. If you create a van and then order;
  the routing is handled for you(It's auto created).</br>
  I've also written util like function; to get the best possible routes; which could also be used as to show shipping options api endpoint for user; if I were to further hone this application. </br>
  


I've actually used google api to analyze distance in miles; and do core stuff with it. <br/>

Make sure; you have tons of vans created; or you might face unexpected issues. I've done my best to cover most of the edge cases; but I might still be <br/> missing some!

Deleting a van- make sure you have enough vans created. so it can reroute to existing vans; and create order with it.<br/>






<b>Make sure you create Van objects first aka drivers before creating orders.<br/>
<b>I've added pricing logic init now, based on how far the location is; it calculates the pricing for you/other cool stuff inside views.py/models.py</b>
