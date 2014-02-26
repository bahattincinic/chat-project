from rest_framework.generics import RetrieveAPIView
from chat.models import User
from .serializers import UserTranslateSerializer
from .permissions import LocalPermission


class TranslateApiView(RetrieveAPIView):
    model = User
    serializer_class = UserTranslateSerializer
    permission_classes = (LocalPermission,)
    lookup_field = "pk"
    lookup_url_kwarg = "pk"