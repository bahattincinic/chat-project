from rest_framework.permissions import BasePermission
from django.conf import settings
from haystack.inputs import Clean


class SearchQueryPermission(BasePermission):
    def has_permission(self, request, view):
        q = request.QUERY_PARAMS.get('q')
        query_length = getattr(settings, "SEARCH_QUERY_LENGTH", 3)
        if not (q and len(Clean(q).query_string) > query_length):
            return False
        return True
