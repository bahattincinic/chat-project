from django.conf import settings
from redis.exceptions import WatchError
from rest_framework.generics import RetrieveAPIView, ListAPIView
from chat.models import User
from .serializers import UserTranslateSerializer
from .permissions import LocalPermission



class TranslateApiView(RetrieveAPIView):
    model = User
    serializer_class = UserTranslateSerializer
    permission_classes = (LocalPermission,)
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        user_id = self.kwargs['pk']
        return User.actives.filter(id=user_id)


class OnlineUsersAPIView(ListAPIView):
    model = User
    serializer_class = UserTranslateSerializer
    permission_classes = (LocalPermission,)

    def get_queryset(self):
        r = redis.StrictRedis()
        ranked_username_set = []
        with r.pipeline() as pipe:
            while 1:
                try:
                    rank_key = getattr(settings, 'REDIS_RANK_KEY', 'active_connections')
                    user_num = getattr(settings, 'REDIS_RANK_MAX_USERS', 30)
                    # watch this user's sessions
                    pipe.watch(rank_key)
                    ranked_username_set = pipe.zrevrangebyscore(name=rank_key, max="+inf",
                                                                min='-inf', start=0,
                                                                num=user_num)
                    break
                except WatchError:
                    continue

        if not ranked_username_set:
            logger.error("Unable to get ranked username set from redis, check redis..")
        return User.objects.filter(username__in=ranked_username_set)