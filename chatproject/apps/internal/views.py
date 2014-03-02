# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import logging
import simplejson as json
from apps.account.models import User
from core.exceptions import OPSException
from .decorators import ensure_request_origin


@ensure_request_origin(['127.0.0.1', '127.0.1.1', '192.168.75.1'])
@require_http_methods(["GET"])
def translate_user_id(request, *args, **kwargs):
    userid = kwargs.get('userid')

    try:
        if not userid:
            raise OPSException("internal: no userid submitted")
        # return username
        username = User.actives.get_or_raise(id=userid).username
    except OPSException, e:
        logging.exception(e.message)
        return HttpResponse(json.dumps({}))
    return HttpResponse(json.dumps({'username': username}))


@ensure_request_origin(['127.0.0.1', '127.0.1.1', '192.168.75.1'])
@require_http_methods(["GET"])
def close_session(request):
    return HttpResponse('ok')
