from django.urls import path
from ros import views

urlpatterns = [
    path('ros/ping', views.RosViews.as_view({'get': 'ping'})),
    path('ros/talk', views.RosViews.as_view({'get': 'talk_ros'})),
]
