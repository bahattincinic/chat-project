# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission
from account.models import User
from actstream.models import action
from network.models import Network, NetworkConnection

SAFE_METHODS = ('GET', 'HEAD')

class NetworkDetailPermission(BasePermission):
    def has_permission(self, request, view):
        network = Network.objects.none()
        pk = None

        try:
            pk = request.parser_context.get("kwargs").get("pk")
            network = Network.objects.get(pk=pk)
            if network.is_public:
                return True
            else:
                # check if user is part of the network
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