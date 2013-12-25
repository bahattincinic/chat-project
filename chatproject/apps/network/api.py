# -*- coding: utf-8 -*-
from rest_framework.generics import ListAPIView, RetrieveAPIView
from network.permissions import NetworkRetrievePermission
from .permissions import NetworkListPermission
from .serializers import NetworkAPISerializer
from .models import Network
from account.models import User


class NetworkAPIView(ListAPIView):
    serializer_class = NetworkAPISerializer
    permission_classes = \
        (NetworkListPermission,)
    model = Network

    def __init__(self):
        self.user_authenticated = False
        self.user = None
        super(NetworkAPIView, self).__init__()

    def get(self, request, *args, **kwargs):
        print "local get"
        self.user_authenticated = request.user.is_authenticated()
        self.user = request.user
        return super(NetworkAPIView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        print "local get query set"
        if self.user_authenticated and self.user and User.actives.filter(id=self.user.id).exists():
            # in here return all
            return Network.objects.all()
        # return only public networks
        return Network.public.all()


class NetworkDetailAPIView(RetrieveAPIView):
    serializer_class = NetworkAPISerializer
    permission_classes = (NetworkRetrievePermission)
    model = Network