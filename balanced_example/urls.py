from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^easy_donor/', include('easy_donor.urls', namespace="easy_donor")),
    url(r'^admin/', include(admin.site.urls)),
)
