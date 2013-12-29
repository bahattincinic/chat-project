# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission
from account.models import User
from actstream.models import action
from network.models import Network, NetworkConnection

SAFE_METHODS = ('GET', 'HEAD')

class NetworkDetailPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.method in SAFE_METHODS:
            # inappropriate request for this
            # permission set
            return False

        network = Network.objects.none()
        pk = None

        try:
            pk = request.parser_context.get("kwargs").get("pk")
            network = Network.objects.get(pk=pk)
            if network.is_public:
                return True
            else:
                # network is private
                # check if user is
                # part of this network
                if request.user \
                    and request.user.is_authenticated() \
                    and NetworkConnection.check_membership(request.user, network):
                    return True
                return False
        except Exception, e:
            action.send(User.get_logger(),
                        verb=User.verbs.get('permission_exception_network'),
                        action_object=network or None,
                        network_pk=pk,
                        message=e.message,
                        description="exception during %s" % \
                                   self.__class__.__name__)
            return False


class NetworkListCreatePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.method == 'POST' \
            and request.user \
            and request.user.is_authenticated() \
            and User.actives.filter(id=request.user.id).exists():
            # TODO: probably we need to check for limits as well
            # i.e maximum number of networks created by user
            return True
        return False
