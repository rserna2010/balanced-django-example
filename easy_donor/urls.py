from django.conf.urls import patterns, url

from easy_donor import views

urlpatterns = patterns('',
                       # ex: /polls/
                       url(r'^$', views.index, name='index'),
                       # ex: /polls/5/
                       url(r'^charities/(?P<charity_id>\d+)/$', views.charity, name='charity'),
                       url(r'^sign_up/$', views.sign_up, name='sign_up'),
                       url(r'^add_bank_account/$', views.add_bank_account, name='add_bank_account'),
                       )