# -*- coding: utf-8 -*-
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Page
from .serializers import PageAPISerializer
from rest_framework.permissions import AllowAny


class PageListAPIView(ListAPIView):
    serializer_class = PageAPISerializer
    permission_classes = (AllowAny,)
    model = Page


class PageDetailAPIView(RetrieveAPIView):
    serializer_class = PageAPISerializer
    permission_classes = (AllowAny,)
    model = Page
    lookup_field = 'slug'