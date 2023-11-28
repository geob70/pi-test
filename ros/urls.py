from django.urls import path
from ros import views

urlpatterns = [
    path("ros/ping", views.RosViews.as_view({"get": "ping"})),
    path("ros/profile", views.RosViews.as_view({"post": "profile", "get": "profile"})),
    path(
        "ros/hotspot-user",
        views.RosViews.as_view({"post": "hotspot_user", "get": "hotspot_user"}),
    ),
]
