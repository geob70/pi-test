from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
import routeros_api


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
    def ping(self, request: Request) -> Response:
        """Test"""
        return Response({"message": "Good response"}, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[permissions.AllowAny],
        serializer_class=[],
        url_path="talk",
    )
    def talk_ros(self, request: Request) -> Response:
        try:
            connection = routeros_api.RouterOsApiPool(
                host="172.16.10.1",
                username="Lantore",
                password="1",
                plaintext_login=True,
            )
            api = connection.get_api()

            # Add a profile with the desired limitations
            profile = api.get_resource(
                "/ip/hotspot/user/profile/add",
                name="profile1",
                rate_limit="256k/512k",
                # shared_users="10",
            )

            # Add a user with the desired profile and limitations
            user = api.get_resource(
                "/ip/hotspot/user/add",
                name="user1",
                password="password1",
                profile="profile1",
            )

            print(user)

            # Close the connection
            connection.disconnect()

            return Response({"data": "user"}, status=status.HTTP_200_OK)
        except ValueError as error:
            return Response(
                {"Error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
