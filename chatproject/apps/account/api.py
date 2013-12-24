from __future__ import absolute_import
import datetime

from django.utils.timezone import utc
from django.conf import settings
from django.contrib.auth import login
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from actstream.models import action, Action
from account.models import User
from api.models import AccessToken
from rest_framework.permissions import AllowAny
from .serializers import UserDetailSerializer


class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token, created = AccessToken.objects.get_or_create(
                user=serializer.object['user'], is_deleted=False)

            if not created:
                # update the created time of the token to keep it valid
                token.created = datetime.datetime.utcnow().replace(tzinfo=utc)
                token.save()

            action.send(serializer.object['user'], verb=User.verbs.get("login"),
                        level=Action.INFO, type=settings.TOKEN_SESSION)
            user_data = UserDetailSerializer(serializer.object['user'])
            return Response({'user': user_data.data, 'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionAuthentication(APIView):
    serializer_class = AuthTokenSerializer
    permission_classes = (AllowAny,)
    model = User

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            login(request, serializer.object['user'])
            action.send(serializer.object['user'], verb=User.verbs.get("login"),
                        level=Action.INFO, type=settings.AUTH_SESSION)
            user_data = UserDetailSerializer(serializer.object['user'])
            return Response(user_data.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)