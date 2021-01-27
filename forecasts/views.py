import requests
import xml.etree.ElementTree as ET
import datetime
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from .models import Location
from .forms import LocationForm
from requests.exceptions import ConnectionError



class HomeView(TemplateView):
    template_name = 'forecasts/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        is_cached = ('geodata' in self.request.session)
        ipstack_api_info = []
        ipstack_api_status = None
        if not is_cached:
            #FOR PRODUCTION -->
            params = {'access_key': settings.IPSTACK_API_KEY}
            ip_address = self.request.META.get('HTTP_X_CLIENT_IP')
            ipstack_api_request = requests.get('http://api.ipstack.com/%s' % ip_address, params=params)
            #FOR LOCAL -->
            # ip_url = 'http://api.ipstack.com/check?access_key=' + settings.IPSTACK_API_KEY
            # ipstack_api_request = requests.get(ip_url)        
            
            #Verify whether or not error occurred with IpStack response   
            ipstack_api_info = get_api_info(ipstack_api_request)
            ipstack_api_status = ipstack_api_info[1] 
            if ipstack_api_status == True:       
                self.request.session['geodata'] = json.loads(ipstack_api_info[0])             

        if ipstack_api_status == False:        
            context = {
                'api':ipstack_api_info[0],
                'apiMsg':ipstack_api_info[2]
            }     
        else:        
            geodata = self.request.session['geodata']
            zipCode = geodata.get('zip')
            
            #Get XML response from NOAA's API - 5 days of forecasts   
            noaa_api_info = get_noaa_data(zipCode)  
			
            #Verify whether or not error occurred with NOAA response                 
            if noaa_api_info[0] == False:       
                context = {
                    'api':False,
                    'apiMsg':noaa_api_info[2]
                } 
            else: 
                dates = noaa_api_info[1]
                maxTemps = noaa_api_info[3][0][0]
                minTemps = noaa_api_info[3][1][0]
                icons = noaa_api_info[3][2][0]
                conditions = noaa_api_info[3][3][0]

                #Zip up the data to use in a for loop for the home view
                allData = list(zip(icons, dates, maxTemps, minTemps, conditions))
                context = {
                    'ip':geodata.get('ip'),
                    'country':geodata.get('country_name', ''),
                    'city':geodata.get('city', ''),
                    'region_code':geodata.get('region_code', ''),        
                    'latitude': geodata.get('latitude', ''),
                    'longitude': geodata.get('longitude', ''),
                    'api_key':settings.GOOGLE_MAPS_API_KEY,
                    'api':True,
                    'apiMsg':'',
                    'today_data':allData[0],
                    'week_data':allData
                } 
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('dashboard')
        return super(HomeView, self).dispatch(self.request, *args, **kwargs)



class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'forecasts/dashboard.html'
    context_object_name = 'locations'
    
    def get_queryset(self):
        return Location.objects.filter(owner=self.request.user)	

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        locations_obj = self.object_list
        if len(locations_obj) > 0:
            loc_list = list(Location.objects.filter(owner = self.request.user).values('zipcode'))
            ziplist = [d["zipcode"] for d in loc_list]
            if len(ziplist) > 1:		
                zipstr = '+'
                zipstr = zipstr.join(ziplist)
            else:
                zipstr = ziplist[0]	
            #Get XML response from NOAA's API - 5 days of forecasts per zipcode
            all_data = get_noaa_data(zipstr)
            if all_data[0] == True:      
                maxTemps = all_data[3][0]
                minTemps = all_data[3][1]
                icons = all_data[3][2]
                conditions = all_data[3][3]
                noaa_data = []
                for d in range(len(ziplist)):
                    newList = []
                    newList = list(zip(maxTemps[d],minTemps[d],icons[d],conditions[d]))
                    noaa_data.append(newList)                    
                context['api'] = True
                context['api_key'] = settings.GOOGLE_MAPS_API_KEY
                context['apiMsg'] = ''	
                context['date_range'] = list(range(len(all_data[1])))
                context['dates'] = all_data[1]
                context['map_points'] = all_data[2]
                context['noaa_data'] = noaa_data
            else:
                context['api'] = False
                context['apiMsg'] = all_data[2]
        else:
            context['api'] = True
            context['noaa_data'] = ''
        return context	



class CreateLocationView(LoginRequiredMixin, CreateView):
    template_name = 'forecasts/add_location.html'
    model = Location
    form_class = LocationForm

    def get_success_url(self):
        return reverse('dashboard')
        
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(CreateLocationView, self).get_form_kwargs(*args, **kwargs)
        kwargs['owner'] = self.request.user
        return kwargs	

    def is_limit_reached(self):
        return Location.objects.filter(owner=self.request.user).count() >= 5

    def post(self, request, *args, **kwargs):
        if self.is_limit_reached():
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            return super().post(request, *args, **kwargs)



class DeleteLocationView(LoginRequiredMixin, DeleteView): 
    template_name = 'forecasts/delete_location.html'   
    model = Location 
    success_url = "dashboard"
    
    def get_success_url(self):
        return reverse(self.success_url)
        


def get_api_info(api_request):
    try:
        api = api_request.content
    except ConnectionError as e:
        api = "error"

    if api == "error" or api is None:   
        api_status = False
        api_msg = "An Error Occurred..."
    else:
        api_status = True
        api_msg = ""
        
    return api, api_status, api_msg



def get_noaa_data(zipstr):
    noaa_data = []
    noaa_url = 'https://graphical.weather.gov/xml/sample_products/browser_interface/ndfdBrowserClientByDay.php?zipCodeList='+ zipstr +'&format=24+hourly&numDays=5'
    noaa_api_request = requests.get(noaa_url)       

    #Verify whether or not error occurred with NOAA response         
    noaa_api_info = get_api_info(noaa_api_request)        
    
    if noaa_api_info[1] == False:       
        noaa_data.extend([ noaa_api_info[1], noaa_api_info[2] ])
        return noaa_data
    else: 
        root = ET.fromstring(noaa_api_info[0])
        #Initialize lists needed to hold API info                
        all_mapPoints = []
        all_max_temps = []
        all_min_temps = []
        all_conditions = []
        all_icons = []
        dates = []

        #Obtain only necessary NOAA API info  
        for data in root.iter('data'):
            for child in data:
                if child.tag == "location":
                    map_data = child
                    mapPoints = []
                    for child in map_data:
                        if child.tag == 'point':
                            mapPoints.append(child.attrib['latitude'])
                            mapPoints.append(child.attrib['longitude'])
                    all_mapPoints.append(mapPoints)
                    
        for child in root.findall("./data/time-layout/[layout-key='k-p24h-n5-1']"):
            time_data = child
            for child in time_data:
                if child.tag == 'start-valid-time':
                    txtStr = child.text
                    date = txtStr[:10]
                    newDate = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y')
                    dates.append(newDate)
                            
        for parameters in root.iter('parameters'):
            maxTemps = []
            minTemps = []
            temps = []
            conditions = []
            icons = []
            for element in parameters:
                if element.tag == 'temperature':
                    for child in element:
                        if child.tag == 'value':
                            temps.append(child.text)                                
                elif element.tag == 'weather':
                    for child in element:
                        if child.tag == 'weather-conditions':
                            attribDict2 = child.attrib
                            conditions.append(attribDict2['weather-summary'])
                elif element.tag == 'conditions-icon':
                    for child in element:
                        if child.tag == 'icon-link':
                            #icons.append(child.text)
                            url = child.text
                            left = 'fcicons/'
                            right = '.jpg'
                            file_name = url[url.index(left)+len(left):url.index(right)]
                            new_url = 'https://forecast.weather.gov/newimages/medium/'+file_name+'.png'
                            icons.append(new_url)
            maxTemps = temps[0:5]
            all_max_temps.append(maxTemps)
            minTemps = temps[5:10]
            all_min_temps.append(minTemps)
            all_conditions.append(conditions)
            all_icons.append(icons)                            
               
        noaa_data.extend([all_max_temps,all_min_temps,all_icons,all_conditions])
        return noaa_api_info[1], dates, all_mapPoints, noaa_data