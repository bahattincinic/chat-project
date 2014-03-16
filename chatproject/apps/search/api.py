# -*- coding: utf-8 -*-
from __future__ import absolute_import
from haystack.inputs import Clean
from haystack.query import SearchQuerySet
from rest_framework.permissions import AllowAny
from rest_framework import generics, status
from rest_framework.response import Response
from django.conf import settings
from account.models import User
from network.models import Network
from .serializers import CombinedSearchResultSerializer
from .models import SearchQuery


class UserSearchAPIView(generics.RetrieveAPIView):
    model = SearchQuerySet
    serializer_class = CombinedSearchResultSerializer
    permission_classes = (AllowAny,)

    def get_object(self, queryset=None):
        query = self.request.QUERY_PARAMS.get('q')
        if not query:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        query = Clean(query)
        limit = getattr(settings, "SEARCH_LIMIT", 5)
        users = SearchQuerySet().filter(content=query).models(User)[:limit]
        networks = SearchQuerySet().filter(content=query).models(Network)[:limit]
        user_pks = [x.pk for x in users]
        network_pks = [x.pk for x in networks]
        search_query = SearchQuery.objects.create(query=query)
        [search_query.users.add(u) for u in User.actives.filter(id__in=user_pks)]
        [search_query.networks.add(u) for u in Network.objects.filter(id__in=network_pks)]
        return search_query
