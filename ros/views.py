from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action, api_view
import routeros_api


def openConnection(data):
    connection = routeros_api.RouterOsApiPool(
        host=data["host"],  # "172.16.10.1"
        username=data["name"],  # "Lantore"
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
        """Check raspberry server avalability"""
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
            shared_users = request.data["shared_users"]

            try:
                # Add a profile with the desired limitations
                profile = api.get_resource("/ip/hotspot/user/profile").add(
                    name=profile_name, rate_limit=rate_limit, shared_users=shared_users
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
        methods=["POST", "PATCH"],
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
                # Update User Profile
                user_profile = api.get_resource("/ip/hotspot/user/profile")
                user_profile.set(
                    id=data["user_id"], name=data["name"], rate_limit=data["rate_limit"]
                )  # "10M/10M"

                # Close the connection
                connection.disconnect()

                return Response(
                    {"message": "User updated", data: user_profile},
                    status=status.HTTP_200_OK,
                )
            except ValueError as error:
                return Response(
                    {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        if request.method == "POST":
            try:
                # All fields are in string format
                profile_name = request.data["profile_name"]
                password = request.data["password"]
                user_name = request.data["user_name"]

                # Add a user with the desired profile and limitations
                user = api.get_resource("/ip/hotspot/user").add(
                    name=user_name, password=password, profile=profile_name
                )

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


@api_view(["GET"])
def get_user_stats(request: Request) -> Response:
    # Fetch User Statistics
    user_id = request.query_params.get("user_id", None)

    connection = openConnection(request.data)
    api = connection.get_api()

    try:
        user = api.get_resource("/ip/hotspot/user")

        # Fetch user stats
        stats = user.get(id=user_id)

        # Close the connection
        connection.disconnect()

        return Response({"stats": stats}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
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

    try:
        # Disable user
        api.get_resource("/ip/hotspot/user").set(name=username, disabled="yes")

        # Close the connection
        connection.disconnect()
        return Response({"message": "User disabled"}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def fetch_data_usage(request: Request) -> Response:
    """fetch user data usage"""

    connection = openConnection(request.data)
    api = connection.get_api()

    userid = request.query_params.get("user_id", None)
    print(userid)

    try:
        if userid is None:
            return Response(
                {"message": "User user_id missing"}, status=status.HTTP_200_OK
            )
        # Fetch data usage per day
        data_usage = api.get_resource("/ip/hotspot/user").get(id=userid, stats="daily")

        # Close the connection
        connection.disconnect()
        return Response({"data_usage": data_usage}, status=status.HTTP_200_OK)
    except ValueError as error:
        return Response(
            {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
