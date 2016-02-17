import os
from datetime import datetime

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django import forms
from django.utils import timezone

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import MeanShift
from sklearn.neighbors.kde import KernelDensity

from app.settings import BASE_DIR

def file_path(filename):
    print(BASE_DIR)
    return (os.path.join(BASE_DIR, 'data', filename))


LOAD_TAXI_DF = False
taxi_df = None
def analysis(lon, lat, day=None, hour=None, distance=1, method=1):
    global LOAD_TAXI_DF, taxi_df

    if not LOAD_TAXI_DF:
        filename = file_path('nyc_data.csv')
        taxi_df = pd.read_csv(filename, parse_dates=['pickup_datetime', 'dropoff_datetime'])
        LOAD_TAXI_DF = True

    columns = ['medallion', 'pickup_datetime', 'dropoff_datetime',
                'pickup_latitude', 'pickup_longitude',
                'dropoff_latitude', 'dropoff_longitude']
    taxi_df = taxi_df[columns]

    target_lat, target_lon = float(lat) , float(lon)
    target_day = datetime.now().weekday() if not day else int(day)
    target_hour = datetime.now().hour if not hour else int(hour)

    width = 0.010 * float(distance)

    lat_max, lon_max = target_lat + width, target_lon - width
    lat_min, lon_min = target_lat - width, target_lon + width 

    hour_day_df = taxi_df[ (taxi_df.pickup_datetime.dt.hour==target_hour) & (taxi_df.pickup_datetime.dt.day==target_day)][['pickup_latitude', 'pickup_longitude']]
    hour_day_df = hour_day_df[(hour_day_df['pickup_latitude'] > lat_min) & (hour_day_df['pickup_latitude'] < lat_max)]
    hour_day_df = hour_day_df[(hour_day_df['pickup_longitude'] < lon_min) & (hour_day_df['pickup_longitude'] > lon_max)]

    if method == 'MeanShift':
        clf = MeanShift().fit(hour_day_df.values)
        centers = clf.cluster_centers_
    elif method == 'KernelDensity':
        clf = KernelDensity(kernel='gaussian', bandwidth=0.005).fit(hour_day_df.values)
        score = clf.score_samples(hour_day_df.values)
        index_score = np.argsort(score)
        centers = hour_day_df[index_score < 20].values
    else:
        clf = AffinityPropagation().fit(hour_day_df.values)
        centers = clf.cluster_centers_

    markers = [{'lon':str(center[0]), 'lat':str(center[1]) } for center in centers]
    return markers

def index(request):
    data = {'day': datetime.now().weekday(),
             'hour': datetime.now().hour,
             'distance':'1',
             'method': 'Affinty'}
    datehourform = DateHourForm(data)
    return render(request, 'nyc/map.html', {'datehourform':datehourform})

class DateHourForm(forms.Form):
    DAY_CHOICE = ((str(i), str(i)) for i in range(1, 8))
    HOUR_CHOICE = ((str(i), str(i)) for i in range(0, 24))
    DISTANCE_CHOICE = ((str(i), str(i)) for i in range(1, 4))
    METHOD_CHOICE = (('Affinty', 'Affinty'), 
                        ('MeanShift', 'MeanShift'),
                        ('KernelDensity', 'KernelDensity'),
                        )

    day = forms.ChoiceField(choices=DAY_CHOICE, required=True)
    hour = forms.ChoiceField(choices=HOUR_CHOICE, required=True)
    distance = forms.ChoiceField(choices=DISTANCE_CHOICE, required=True)
    method = forms.ChoiceField(choices=METHOD_CHOICE, required=True)

@csrf_exempt
def get_recommends(request):
    if request.method == 'POST':
        lon = request.POST.get('lon')
        lat = request.POST.get('lat')
        day = request.POST.get('day')
        hour = request.POST.get('hour')
        distance = request.POST.get('distance') or '1'
        method = request.POST.get('method') or 'Affinty'
        markers = analysis(lon, lat, day, hour, distance, method)
        return JsonResponse({'result':'ok', 'markers': markers})
