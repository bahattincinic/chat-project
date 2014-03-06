from django.http.response import Http404
import redis
import logging
from django.conf import settings
from redis.exceptions import WatchError
from rest_framework import generics
from rest_framework.permissions import AllowAny
from account.models import User
from account.serializers import AnonUserDetailSerializer
from network.models import Network


logger = logging.getLogger(__name__)


def get_ranks():
    rank_key = getattr(settings, 'REDIS_RANK_KEY', 'active_connections')
    user_num = getattr(settings, 'REDIS_RANK_MAX_USERS', 30)
    r = redis.StrictRedis()
    username_set = []
    with r.pipeline() as pipe:
        while 1:
            try:
                # watch this user's sessions
                pipe.watch(rank_key)
                username_set = pipe.zrevrangebyscore(name=rank_key, max="+inf",
                                                     min='-inf', start=0,
                                                     num=user_num)
                break
            except WatchError:
                continue
    if not username_set:
        logger.error("Unable while getting ranked users from redis, "
                     "empty or invalid list, rank_key: %s" % rank_key)
    return username_set or []


class ShuffleAPIView(generics.ListAPIView):
    model = User
    serializer_class = AnonUserDetailSerializer
    # TODO: to be changed later
    permission_classes = (AllowAny,)

    def get_queryset(self):
        username_set = get_ranks()
        if not username_set:
            return Http404()
        return User.objects.filter(username__in=username_set).order_by('?')


class NetworkShuffleApiView(generics.ListAPIView):
    model = User
    serializer_class = AnonUserDetailSerializer
    # TODO: to be changed later, check for network permissions
    permission_classes = (AllowAny,)

    def get_queryset(self):
        username_set = get_ranks()

        try:
            slug = self.kwargs.get('slug')
            network = Network.objects.get_or_raise(slug=slug)
        except:
            raise Http404()
        return User.objects.filter(username__in=username_set,
                                   networkconnection__network=network)\
            .order_by('?')