"""pFinalSat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
import parking.views as pview


urlpatterns = [
    url(r'^$', pview.barra, name="Main Page"),
    url(r'^xml$', pview.barraxml, name="Main Page XML"),
    url(r'^json$', pview.barrajson, name="Main Page JSON"),
    url(r'^rss$', pview.canalRSS, name="Main Page"),
    url(r'^parser$', pview.parseador, name="Parser of database"),
    url(r'^aparcamientos/(\d+)$', pview.individualParking, name="Individual Parking Page"),
    url(r'^aparcamientos$', pview.parkings, name="Parkings Page"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about$', pview.about, name="Info App"),
    url(r'^logout$', pview.myLogout, name="Logout"),
    url(r'^login', pview.myLogin, name="Login"),
    url(r'^prueba.css', pview.linkcss, name="Return the css"),
    url(r'^css', pview.changeUserData, name="Change the data of users"),
    url(r'^(.+)/xml$', pview.userxml, name="User Page XML"),
    url(r'^(.+)/json$', pview.userjson, name="User Page JSON"),
    url(r'^(.+)$', pview.user, name="User Page"),
    ]
