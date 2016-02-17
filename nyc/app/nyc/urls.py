from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^get_recommends$', views.get_recommends, name='get_recommends'),
]

