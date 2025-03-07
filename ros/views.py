from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action, api_view
import routeros_api


def openConnection(data):
    connection = routeros_api.RouterOsApiPool(
        host=data["host"],  # "172.16.10.1"
        username=data["hostname"],  # "Lantore"
        password=data["password"],  # "1"
        plaintext_login=True,
    )
    return connection


class RosViews(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    authentication_classes = ()
    serializer_class = ()

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[permissions.AllowAny],
        serializer_class=[],
        url_path="ping",
    )
    def ping(self, _: Request) -> Response:
        """Check raspberry server availability"""
        return Response({"message": "Good response"}, status=status.HTTP_200_OK)

    @action(
        methods=["POST", "GET"],
        detail=False,
        permission_classes=[permissions.AllowAny],
        serializer_class=[],
        url_path="profile",
    )
    def profile(self, request: Request) -> Response:
        """Hotspot profile"""
        connection = openConnection(request.data)
        api = connection.get_api()

        if request.method == "POST":
            # All fields are in string format
            profile_name = request.data["profile_name"]
            rate_limit = request.data["rate_limit"]  # e.g 2048000 for 2gb
            # shared_users = request.data["shared_users"]

            try:
                # Add a profile with the desired limitations
                profile = api.get_resource("/ip/hotspot/user/profile").add(
                    name=profile_name.encode(), rate_limit=rate_limit.encode()
                )

                # Close the connection
                connection.disconnect()

                return Response(
                    {"message": "Profile created successfully", "data": profile},
                    status=status.HTTP_200_OK,
                )
            except ValueError as error:
                return Response(
                    {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        if request.method == "GET":
            try:
                # Fetch List/Resource
                list = api.get_resource("/ip/hotspot/user/profile")
                profiles = list.get()

                # Close the connection
                connection.disconnect()
                return Response({"profiles": profiles}, status=status.HTTP_200_OK)
            except ValueError as error:
                return Response(
                    {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    @action(
        methods=["POST", "PATCH", "GET"],
        detail=False,
        permission_classes=[permissions.AllowAny],
        serializer_class=[],
        url_path="hotspot-user",
    )
    def hotspot_user(self, request: Request) -> Response:
        """Create a hotspot user profile"""
        connection = openConnection(request.data)
        api = connection.get_api()

        data = request.data

        if request.method == "PATCH":
            try:
                # Get the ID of the user
                user = api.get_resource("/ip/hotspot/user").get(
                    name=data["old_username"]
                )[0]

                user_id = user["id"]
                # Update the password of the user
                api.get_resource("/ip/hotspot/user").set(
                    id=user_id, name=data["new_username"]
                )
                # Close the connection
                connection.disconnect()

                return Response(
                    {"message": "User updated"},
                    status=status.HTTP_200_OK,
                )
            except ValueError as error:
                return Response(
                    {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        if request.method == "POST":
            try:
                # All fields are in string format
                # profile_name = request.data["profile_name"]
                password = request.data["user_password"]
                user_name = request.data["username"]

                # Add a user with the desired profile and limitations
                api.get_resource("/ip/hotspot/user").add(
                    name=user_name,
                    password=password,
                    limit_bytes_total="0",
                )

                # Fetch user
                user = api.get_resource("/ip/hotspot/user").get(name=user_name)[0]
                api.get_resource("/ip/hotspot/user").set(id=user["id"], disabled="yes")
                # Close the connection
                connection.disconnect()

                return Response(
                    {"message": "user created successfully", "data": user},
                    status=status.HTTP_200_OK,
                )
            except ValueError as error:
                return Response(
                    {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    @action(
        methods=["POST", "PATCH", "GET"],
        detail=False,
        permission_classes=[permissions.AllowAny],
        serializer_class=[],
        url_path="users",
    )
    def users(self, request: Request) -> Response:
        """Users endpoint"""
        connection = openConnection(request.data)
        api = connection.get_api()

        try:
            # Fetch All Users
            users = api.get_resource("/ip/hotspot/user")
            all_users = users.get()

            # Close the connection
            connection.disconnect()

            return Response({"users": all_users}, status=status.HTTP_200_OK)
        except ValueError as error:
            return Response(
                {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[permissions.AllowAny],
        serializer_class=[],
        url_path="data-usage",
    )
    def check_all_active_user_data_usage(self, request: Request) -> HttpResponse:
        """check all active user data usage"""

        connection = openConnection(request.data)
        api = connection.get_api()

        try:
            # Fetch active users
            active_users = api.get_resource("/ip/hotspot/active").get()
            users_data = []

            for user in active_users:
                # Fetch data usage
                data_used = int(user["bytes-out"]) + int(user["bytes-in"])
                users_data.append(
                    {
                        "data_used": data_used,
                        "user_name": user["user"],
                        "uptime": user["uptime"],
                        "server": user["server"],
                        "mac_address": user["mac-address"],
                        "address": user["address"],
                    }
                )
            # Close the connection
            connection.disconnect()
            return Response(
                {"users": users_data, "active_users": len(users_data)},
                status=status.HTTP_200_OK,
            )
        except ValueError as error:
            return Response(
                {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["POST"])
def get_user_data(request: Request) -> Response:
    # Fetch User Statistics
    connection = openConnection(request.data)
    api = connection.get_api()

    username = request.data["username"]

    try:
        user = api.get_resource("/ip/hotspot/user").get(name=username)[0]

        # Close the connection
        connection.disconnect()
        return Response(
            {"message": "User data fetched", "user": dict(user)},
            status=status.HTTP_200_OK,
        )
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
def get_active_users(request: Request) -> Response:
    """Fetch Active users"""

    connection = openConnection(request.data)
    api = connection.get_api()

    try:
        # Fetch active users
        active_users = api.get_resource("/ip/hotspot/active").get()

        # Close the connection
        connection.disconnect()
        return Response({"active_users": active_users}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
def disable_user(request: Request) -> Response:
    """Disable user"""

    connection = openConnection(request.data)
    api = connection.get_api()

    username = request.data["username"]
    is_disabled = request.data["is_disabled"]

    try:
        user = api.get_resource("/ip/hotspot/user").get(name=username)[0]
        api.get_resource("/ip/hotspot/user").set(id=user["id"], disabled=is_disabled)

        # Close the connection
        connection.disconnect()
        return Response({"message": "User disabled"}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
def check_data_usage(request: Request) -> Response:
    """fetch user data usage"""

    connection = openConnection(request.data)
    api = connection.get_api()

    username = request.data["username"]
    limit = request.data["limit"]

    try:
        # Get User
        user = api.get_resource("/ip/hotspot/user").get(name=username)[0]
        user_id = user["id"]

        # Fetch data usage per day
        data_used = int(user["bytes-out"]) + int(user["bytes-in"])

        if data_used >= int(limit):
            # Disable user
            api.get_resource("/ip/hotspot/user").set(id=user_id, disabled="yes")
            connection.disconnect()
            return Response(
                {"data_used": data_used, "disabled": True}, status=status.HTTP_200_OK
            )

        # Close the connection
        connection.disconnect()
        return Response(
            {"data_used": data_used, "disabled": False}, status=status.HTTP_200_OK
        )
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
def get_user_connected_devices(request: Request) -> Response:
    """Fetch user connected devices"""

    connection = openConnection(request.data)
    api = connection.get_api()

    user_name = request.query_params.get("user_name", None)

    try:
        # Fetch user connected devices
        user_devices = api.get_resource("/ip/hotspot/active").get(user=user_name)

        # # Get the IP address of the user
        # user_resource = api.get_resource("/tool/user-manager/user")
        # user_data = user_resource.get(id=user_id)[0]
        # user_ip = user_data["ip-address"]

        # Get the MAC addresses of devices connected to the router
        # arp_resource = api.get_resource("/ip/arp")
        # arp_data = arp_resource.get()

        # print(arp_data)
        # user_devices = [
        #     entry["mac-address"] for entry in arp_data if entry["address"] == user_ip
        # ]

        # Close the connection
        connection.disconnect()
        return Response(
            {
                "user_devices": user_devices,
            },
            status=status.HTTP_200_OK,
        )
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
def delete_hotspot_user(request: Request) -> Response:
    """Delete hotspot user"""

    connection = openConnection(request.data)
    api = connection.get_api()

    user_id = request.query_params.get("user_id", None)
    username = request.data["username"]
    user = api.get_resource("/ip/hotspot/user").get(name=username)[0]

    try:
        # Delete user
        api.get_resource("/ip/hotspot/user").remove(id=user_id)

        # Close the connection
        connection.disconnect()
        return Response({"message": "User deleted"}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
def delete_hotspot_user_by_name(request: Request) -> Response:
    """Delete hotspot user"""

    connection = openConnection(request.data)
    api = connection.get_api()

    username = request.data["username"]

    try:
        # Delete user
        user = api.get_resource("/ip/hotspot/user").get(name=username)[0]
        user_id = user["id"]
        api.get_resource("/ip/hotspot/user").remove(id=user_id)

        # Close the connection
        connection.disconnect()
        return Response({"message": "User deleted"}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
def change_password(request: Request) -> Response:
    """Change user password"""

    connection = openConnection(request.data)
    api = connection.get_api()

    password = request.data["new_password"]
    username = request.data["username"]

    try:
        # Get the ID of the user
        user = api.get_resource("/ip/hotspot/user").get(name=username)[0]

        user_id = user["id"]
        # Update the password of the user
        api.get_resource("/ip/hotspot/user").set(id=user_id, password=password)

        # Close the connection
        connection.disconnect()
        return Response({"message": "Password updated"}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
def reset_data_usage(request: Request) -> Response:
    """Reset data usage for user"""

    connection = openConnection(request.data)
    api = connection.get_api()
    username = request.data["username"]

    # Get the ID of the user
    user = api.get_resource("/ip/hotspot/user").get(name=username)[0]
    user_id = user["id"]

    # Reset the data usage of the user
    try:

        # if user:
        #     # Reset bytes in/out to zero
        #     api.get_resource("/ip/hotspot/user").set(id=user_id, bytes=0)
        #     return Response({"message": "reset complete"}, status=status.HTTP_200_OK)

        # Check if the user exists in PPP secrets
        ppp_users = api.get_resource("/ppp/secret").get(name=username)[0]
        ppp_users_id = ppp_users["id"]

        if ppp_users:
            # Reset bytes in/out to zero
            api.get_resource("/ppp/secret").set(id=ppp_users_id, bytes=0)
            return Response(
                {"message": "reset complete on ppp_users"}, status=status.HTTP_200_OK
            )

        return Response({"message": "reset not found"}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        # Disconnect from the router
        connection.disconnect()


@api_view(["POST"])
def set_data_limit(request: Request) -> Response:
    """Set data limit for user"""

    connection = openConnection(request.data)
    api = connection.get_api()

    limit_bytes_total = request.data["limit_bytes_total"]
    username = request.data["username"]

    try:
        # Get the ID of the user
        user = api.get_resource("/ip/hotspot/user").get(name=username)[0]

        user_id = user["id"]
        # Update the password of the user
        api.get_resource("/ip/hotspot/user").set(
            id=user_id, limit_bytes_total=limit_bytes_total
        )

        # Close the connection
        connection.disconnect()
        return Response({"message": "Data limit updated"}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
def remove_device(request: Request) -> Response:
    """Remove device from hotspot"""

    connection = openConnection(request.data)
    api = connection.get_api()

    mac_address = request.data["mac_address"]

    try:
        result = api.get_resource("/ip/hotspot/active").get(mac_address=mac_address)

        # Remove the session if found
        if result:
            api.get_resource("/ip/hotspot/active").remove(id=result[0]["id"])
            # Close the connection
            connection.disconnect()
            return Response({"message": "Device removed"}, status=status.HTTP_200_OK)

        # Close the connection
        connection.disconnect()
        return Response({"message": "No Device found"}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
def assign_profile(request: Request) -> Response:
    """Assign profile to user"""

    connection = openConnection(request.data)
    api = connection.get_api()

    profile_name = request.data["profile_name"]
    username = request.data["username"]

    try:
        # Get the ID of the user
        user = api.get_resource("/ip/hotspot/user").get(name=username)[0]

        user_id = user["id"]
        # Update the password of the user
        api.get_resource("/ip/hotspot/user").set(id=user_id, profile=profile_name)

        # Close the connection
        connection.disconnect()
        return Response({"message": "Profile assigned"}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
