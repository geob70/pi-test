from django.urls import path
from ros import views
from ros.views import get_user_stats, get_active_users, disable_user, fetch_data_usage

urlpatterns = [
    path("ros/ping", views.RosViews.as_view({"get": "ping"})),
    path("ros/users", views.RosViews.as_view({"get": "users"})),
    path("ros/profile", views.RosViews.as_view({"post": "profile", "get": "profile"})),
    path(
        "ros/hotspot-user",
        views.RosViews.as_view({"post": "hotspot_user", "get": "hotspot_user"}),
    ),
    path("ros/user-stats/", get_user_stats, name="user-stats"),
    path("ros/active-users/", get_active_users, name="active-user"),
    path("ros/disable-user/", disable_user, name="disable-user"),
    path("ros/data-usage/", fetch_data_usage, name="fetch_data_usage"),
]
