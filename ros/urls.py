from django.urls import path
from ros import views
from ros.views import (
    assign_profile,
    change_password,
    # check_all_active_user_data_usage,
    delete_hotspot_user,
    delete_hotspot_user_by_name,
    get_user_connected_devices,
    get_user_data,
    get_active_users,
    disable_user,
    check_data_usage,
    remove_device,
    reset_data_usage,
    set_data_limit,
)

urlpatterns = [
    path("ros/ping", views.RosViews.as_view({"get": "ping"})),
    path("ros/users", views.RosViews.as_view({"post": "users"})),
    path("ros/profile", views.RosViews.as_view({"post": "profile", "get": "profile"})),
    path(
        "ros/hotspot-user",
        views.RosViews.as_view({"post": "hotspot_user", "patch": "hotspot_user"}),
    ),
    path("ros/user", get_user_data, name="user-data"),
    path("ros/active-users", get_active_users, name="active-user"),
    path("ros/disable-user", disable_user, name="disable-user"),
    path("ros/data-usage", check_data_usage, name="check_data_usage"),
    path(
        "ros/user-connected-devices",
        get_user_connected_devices,
        name="get-user-connected-devices",
    ),
    path("ros/delete-hotspot-user", delete_hotspot_user, name="delete_hotspot_user"),
    path("ros/change-user-password", change_password, name="change_password"),
    path("ros/set-data-limit", set_data_limit, name="set_data_limit"),
    path(
        "ros/check-all-active-users-usage",
        views.RosViews.as_view(
            {
                "post": "check_all_active_user_data_usage",
            }
        ),
    ),
    path("ros/remove-device", remove_device, name="remove_device"),
    path("ros/assign-profile", assign_profile, name="assign_profile"),
    path("ros/delete-user", delete_hotspot_user_by_name, name="delete_user"),
    path("ros/reset-data", reset_data_usage, name="reset_data_usage"),
]
