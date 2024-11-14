from django.urls import path
from  restaurant import views


urlpatterns=[
    path('',views.RestaurantListView.as_view(),name='restaurant_list'),
]