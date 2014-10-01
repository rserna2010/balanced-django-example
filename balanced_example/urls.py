from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'balanced_example.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^easy_donor/', include('easy_donor.urls', namespace="easy_donor")),
    url(r'^admin/', include(admin.site.urls)),
)
