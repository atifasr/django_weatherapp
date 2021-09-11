from asyncio.tasks import create_task, sleep
from django.contrib.messages.api import add_message
from django.http import response
from django.shortcuts import redirect, render
import asyncio
from .helpers import kelvin_to_celisus,UtcToIst
import aiohttp
from .helpers import ConverTime
import datetime as dt
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async
import pickle
from django.contrib import messages
# Create your views here.


def index(request):
    city_ = request.COOKIES.get('city_name')
    if city_:
        request.session['city_name']=city_
        return redirect(f'/fetch_weather/?city={city_}')

    return render(request,'weather/base.html')





async def get_forecastweather(city_name,key):
    url = 'http://'+'api.openweathermap.org/data/2.5/forecast?q'
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{url}={city_name}&appid={key}') as response:
            data = await response.json()
            return data




async def getcurrent_weather(city_name,country_code,key):
    state_code = ''
    url = 'http://'+'api.openweathermap.org/data/2.5/weather?q'
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{url}={city_name},{state_code},{country_code}&appid={key}') as response:
            if response.status != 404:
                data = await response.json()
                return data
            else:
                return None





#view for fetching weather

def fetch_weather(request):
    if request.method == 'GET':
        city_name = request.GET.get('city')
        key = '48cae9af5bbad31b93b51b6db42dea12'

        if 'country_code' in request.GET:
            country_code = request.GET.get('country_code')
        else:
            country_code = None
        
        current_weather  = asyncio.run(getcurrent_weather(city_name,country_code,key))
        forecast_weather  = asyncio.run(get_forecastweather(city_name,key))
        keys = current_weather
        if keys!= None:
            data ={}
            data['date'] = keys['dt']
            data['city_name']=keys['name']
            data['description']=keys['weather'][0]['description']
            data['temp'] = round(kelvin_to_celisus(keys['main']['temp']),2) 
            data['feels_like'] = round(kelvin_to_celisus(keys['main']['feels_like']),2)
            data['max_temp'] = round(kelvin_to_celisus(keys['main']['temp_max']),2)
            data['min_temp'] = round(kelvin_to_celisus(keys['main']['temp_min']),2)
            data['sunrise'] = ConverTime(UtcToIst(keys['sys']['sunrise'])) 
            data['sunset'] = ConverTime(UtcToIst(keys['sys']['sunset']))

        # print(data)

            forecast = {}
            for keys,values in forecast_weather.items():
                if keys == 'list':
                    forecast['forecast'] = values
                if keys == 'city':
                    forecast['city'] = values



 # modifying forecast data removing redundancies 
            updated_forcast = {}
            updated_forcast['forecast'] = []
            date_changed = False

            prev = None
            for items in forecast['forecast']:

                for key,value in items.items():
                    #modifying date value and comparing it as well
                    if key == 'dt_txt':
                        items[key] = dt.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
                        date_ = items[key].date()
                        if prev != date_:
                            date_changed = True
                            
                        prev = date_
                if date_changed:    
                    updated_forcast['forecast'].append(items)
                    date_changed = False

                   
     

            for items in updated_forcast['forecast']:
            
                for key,value in items.items():
                    if key == 'dt_txt':
                        items['dt'] = UtcToIst(items['dt']).split(' ')[0]
                        items['main']['date'] = items[key].date()
                        items['main']['day'] = items[key].strftime("%A")
                        items['main']['temp'] = kelvin_to_celisus(items['main']['temp'])
                        items['main']['temp_min'] = kelvin_to_celisus(items['main']['temp_min'])
                        items['main']['feels_like'] = kelvin_to_celisus(items['main']['feels_like'])
                        items['main']['temp_max'] = kelvin_to_celisus(items['main']['temp_max'])

            updated_forcast['city'] = forecast['city']
            updated_forcast['city']['sunrise'] = ConverTime(UtcToIst(updated_forcast['city']['sunrise']))     
            updated_forcast['city']['sunset'] = ConverTime(UtcToIst(updated_forcast['city']['sunset']))   
            
            session_data = json.dumps(updated_forcast.copy(),indent=4, sort_keys=True, default=str)
            request.session['data'] = session_data
            
            data['date'] = UtcToIst(data['date']).split(' ')[0]
        else:
            data = None
            updated_forcast = None
            messages,add_message(request,messages.INFO,'Unable to find the city')
            
        context ={
            'data': data,
            'forecast':updated_forcast
        }
        return render(request,'weather/base.html',context)



# get location details using position coordinates
async def get_location_iq(key,longi,lati):
    url = f'https://us1.locationiq.com/v1/reverse.php?key={key}&lat={lati}&lon={longi}&format=json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            data = await response.json()
            return data


#getting position coordinates
import json
import concurrent.futures 
@csrf_exempt
def get_location(request):
    if request.method == 'POST':
        key = 'pk.736fba620749123a25d7355ff16b2e52'
        get_data = json.loads(request.body.decode('utf-8'))
        result = asyncio.run(get_location_iq(key,get_data['longitude'],get_data['latitude']))       
        data = result
        return JsonResponse(data,safe=False)
        





def weather_detail(request):
    if request.method == 'GET':
        forecast_data = json.loads(request.session['data'])
        filter_date = request.GET.get('date')
        data_context = None
        if filter_date:
        
            for data in forecast_data['forecast']:
                if data['dt'] == filter_date:
                    data_context = data
                    break
      
        data ={}
        data['city'] = forecast_data['city']
        data['forecast'] = data_context

        return render(request,'weather/weather_detail.html',data)