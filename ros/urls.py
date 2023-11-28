from django.urls import path
from ros import views
from ros.views import get_user_stats

urlpatterns = [
    path("ros/ping", views.RosViews.as_view({"get": "ping"})),
    path("ros/users", views.RosViews.as_view({"get": "users"})),
    path("ros/profile", views.RosViews.as_view({"post": "profile", "get": "profile"})),
    path(
        "ros/hotspot-user",
        views.RosViews.as_view({"post": "hotspot_user", "get": "hotspot_user"}),
    ),
    path("ros/user-stats/", get_user_stats, name="user-stats"),
]
