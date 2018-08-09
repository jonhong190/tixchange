from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^$', views.index),
    url(r'^new_register/$', views.new_register),
    url(r'^register/$', views.register),
    url(r'^login/$', views.login),
    url(r'^main_tix_page/$', views.main_tix_page),
    url(r'^add_ticket/$', views.add_ticket),
    url(r'^add_ticket_process/$', views.add_ticket_process),
    url(r'^user_profile/(?P<id>\d+)$', views.user_profile),
    url(r'^your_profile/(?P<id>\d+)$', views.your_profile),
    url(r'^buy/(?P<ticket_id>\d+)$', views.buy),
    url(r'^offer/(?P<ticket_id>\d+)$', views.offer),
    url(r'^send_offer/$', views.send_offer),
    url(r'^logout/$', views.logout),
    url(r'^remove_offer/(?P<offer_id>\d+)$', views.remove_offer),
    url(r'^accept_offer/(?P<offer_id>\d+)$', views.accept_offer),
    url(r'^accept_offer_proccess$', views.accept_offer_proccess),
    url(r'^delete_ticket/(?P<ticket_id>\d+)$', views.delete_ticket),
    url(r'^edit/(?P<ticket_id>\d+)$', views.edit),
    url(r'^edit_ticket_process/$', views.edit_ticket_process),
    url(r'^buy_process/$', views.buy_process),
    url(r'^main_tix_page/search_events$', views.search_events)
]