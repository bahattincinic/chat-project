from rest_framework import mixins
from rest_framework.generics import GenericAPIView


class ListCreateDestroyAPIView(mixins.DestroyModelMixin,
                               mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               GenericAPIView):
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)