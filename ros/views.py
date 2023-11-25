from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
import ros_api


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
            router = ros_api.Api('172.16.10.1', user='Lantore', password='1')
            r = router.talk('/ip/hotspot/active')
            # hd508aezw2m.sn.mynetname.net
            # 102.215.57.75

            # print(r)
            return Response({'data': r}, status=status.HTTP_200_OK)
        except ValueError as error:
            return Response({'Error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
