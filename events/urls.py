from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('home/', views.index, name='home'),
    path('events/', views.all_events, name='all_events'),
    path('create_event/', views.create_event, name='create_event'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/view/', views.event_view, name='event_view'),
    path('event/<int:event_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.user_cart, name='user_cart'),
    # path('ticketmaster/<str:city>/', views.get_ticketmaster_events, name='ticketmaster-city')
    # 21.08 maiken:
    # path('ticketmaster_event/<str:event_id>/', views.ticketmaster_event_detail, name='ticketmaster_event_detail'),

]

