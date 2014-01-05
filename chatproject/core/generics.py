from rest_framework import mixins
from rest_framework.generics import GenericAPIView


class CreateDestroyAPIView(mixins.DestroyModelMixin,
                           mixins.CreateModelMixin,
                           GenericAPIView):
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)