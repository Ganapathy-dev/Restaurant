from django.urls import path
from  restaurant import views


urlpatterns=[
    path('',views.RestaurantListView.as_view(),name='restaurant_list'),
    path('<int:pk>/',views.RestaurantDetailView.as_view(),name='restaurant_detail'),
    path('bookmark/<int:restaurant_id>/',views.ToggleBookmarkView.as_view(),name='toggle_bookmark'),
    path('visited/<int:restaurant_id>/',views.ToggleVisitedView.as_view(),name='toggle_visited'),

]