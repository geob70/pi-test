from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action


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
    def ping(self, request) -> Response:
        """Test"""
        return Response({"message": "Good response"}, status=status.HTTP_200_OK)
