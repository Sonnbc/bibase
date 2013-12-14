from django.conf.urls import patterns, url, include

from bib import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^getbib/$', views.getbib, name='getbib'),
)    