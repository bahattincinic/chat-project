from __future__ import absolute_import
import datetime
import uuid
import simplejson

from django.utils.timezone import utc
from django.conf import settings
from django.contrib.auth import login, logout
from django.db import transaction
from django.template import Context
from django.template.loader import get_template
from django.core.cache import cache
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from actstream.models import action, Action
from account.models import User
from core.exceptions import OPSException
from api.models import AccessToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from . import serializers
from .permissions import UserCreatePermission, UserDetailPermission


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
            user_data = serializers.UserDetailSerializer(serializer.object['user'])
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
            user_data = serializers.UserDetailSerializer(serializer.object['user'])
            return Response(user_data.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionLogout(APIView):
    permission_classes = (IsAuthenticated,)
    model = User

    def get(self, request):
        user = request.user
        logout(request)
        action.send(user, verb=User.verbs.get('logout'), level=Action.INFO)
        return Response(status=status.HTTP_200_OK)


class TokenLogout(APIView):
    permission_classes = (IsAuthenticated,)
    model = User

    def get(self, request):
        auth = request.auth
        auth.is_deleted = True
        auth.deleted_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        auth.save()
        action.send(request.user, verb=User.verbs.get('logout'),
                    level=Action.INFO, action_object=auth,
                    auth_key=auth.key)
        return Response(status=status.HTTP_200_OK)


class ForgotMyPassword(APIView):
    permission_classes = (AllowAny,)
    model = User

    def post(self, request):
        user = User.objects.none()
        content = ""
        data = None
        try:
            with transaction.atomic():
                serializer = serializers.ForgotMyPasswordSerializer(
                    data=request.DATA)
                if not serializer.is_valid():
                    data = serializer.errors
                    raise OPSException()
                # set secret key
                user = serializer.object.get('user')
                user.secret_key = uuid.uuid4()
                user.save()
                # Template
                template = get_template('email/forgot_my_password.html')
                template_context = Context({'user': user, 'request': request})
                content = template.render(template_context)
        except OPSException:
            statu = status.HTTP_400_BAD_REQUEST
        else:
            statu = status.HTTP_200_OK
            # log
            action.send(user, verb=User.verbs.get('forgot_password'),
                        code='%s' % user.secret_key, content=content,
                        level=Action.INFO)
            # cache
            mail_data = {'content': content, 'to': user.email,
                         'subject': 'Forgot my password'}
            cache.set('forgot_my_password_%s' % user.id,
                      simplejson.dumps(mail_data))
        return Response(data=data, status=statu)

    def put(self, request):
        user = User.objects.none()
        data = None
        try:
            with transaction.atomic():
                serializer = serializers.NewPasswordSerializer(
                    data=request.DATA)
                if not serializer.is_valid():
                    data = serializer.errors
                    raise OPSException()
                user = serializer.object.get('user')
                user.set_password(serializer.data.get('new_password'))
                user.secret_key = ''
                user.save()
        except OPSException:
            statu = status.HTTP_400_BAD_REQUEST
        else:
            statu = status.HTTP_200_OK
            action.send(user, verb=User.verbs.get('new_password'),
                        level=Action.INFO)
        return Response(data=data, status=statu)


class AccountDetail(APIView):
    permission_classes = (UserCreatePermission, UserDetailPermission,)
    model = User
    serializer_class = serializers.UserDetailSerializer

    def get(self, request):
        user_data = self.serializer_class(instance=request.user)
        return Response(user_data.data)

    def put(self, request):
        user = request.user
        data = None
        try:
            with transaction.atomic():
                serializer = self.serializer_class(
                    instance=user, data=request.DATA,
                    files=request.FILES, partial=False)
                if not serializer.is_valid():
                    data = serializer.errors
                    raise OPSException()
                # TODO: Frontend yazilirken file upload testi yapilmali
                # TODO: save yaparken avatar path inin ayarlanmasi
                serializer.save(force_update=True)
                data = serializer.data
        except OPSException:
            statu = status.HTTP_400_BAD_REQUEST
        else:
            statu = status.HTTP_200_OK
            old_profile = simplejson.dumps(
                self.serializer_class(instance=request.user).data)
            action.send(user, verb=User.verbs.get('update'), level=Action.INFO,
                        old_profile=old_profile)
        return Response(data=data, status=statu)

    def post(self, request):
        user = User.objects.none()
        data = None
        try:
            with transaction.atomic():
                serializer = serializers.UserRegister(data=request.DATA)
                if not serializer.is_valid():
                    data = serializer.errors
                    raise OPSException()
                user = User.objects.create_user(
                    is_sound_enabled=True, follow_needs_approve=True,
                    status=User.CHAT_ACTIVE, **serializer.data)
                data = self.serializer_class(instance=user).data
        except OPSException:
            statu = status.HTTP_400_BAD_REQUEST
        else:
            statu = status.HTTP_201_CREATED
            action.send(user, verb=User.verbs.get('register'),
                        level=Action.INFO)
        return Response(data=data, status=statu)

    def delete(self, request):
        user = request.user
        try:
            with transaction.atomic():
                user.is_deleted = True
                user.save()
                # session logout
                logout(request)
                # token logout
                tokens = user.get_active_tokens()
                tokens.select_for_update().update(is_deleted=True)
        except:
            statu = status.HTTP_400_BAD_REQUEST
        else:
            statu = status.HTTP_200_OK
            action.send(user, verb=User.verbs.get('delete'))
        return Response(status=statu)
