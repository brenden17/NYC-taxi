# NYC taxi

This is a small Django application which recommends pickup location for taxi based on some machine learning methods such as Affinty, MeanShift, and KernelDensity.

Dateset is from http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml.

## Requirements

* Python library

~~~
Django==1.9.2
argparse==1.2.1
numpy==1.10.4
pandas==0.17.1
python-dateutil==2.4.2
pytz==2015.7
scikit-learn==0.17
scipy==0.17.0
six==1.10.0
wsgiref==0.1.2

~~~

![alt text](https://github.com/brenden17/NYC-taxi/blob/master/nyc/img/nyc.png "image")

![alt text](https://github.com/brenden17/NYC-taxi/blob/master/nyc/img/density.png "image")
