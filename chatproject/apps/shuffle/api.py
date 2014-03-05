from rest_framework import generics
from rest_framework.permissions import AllowAny
from account.serializers import AnonUserDetailSerializer


class ShuffleAPIView(generics.RetrieveAPIView):
    serializer_class = AnonUserDetailSerializer
    permission_classes = (AllowAny,)