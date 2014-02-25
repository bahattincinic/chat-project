import logging
from django.http.response import HttpResponseNotAllowed
from django.utils.decorators import available_attrs
from functools import wraps


logger = logging.getLogger('internal.decorators')

def ensure_request_origin(origin_list):
    """
    make sure that only requests originating from 'origin_list' can make it into
    view only
    """

    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            print 'allow from %s' % origin_list
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[-1].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')
            if not str(ip) in origin_list:
                logger.error("Deny ip: %s from reaching internal api" % str(ip))
                return HttpResponseNotAllowed('noop')
            return func(request, *args, **kwargs)
        return inner
    return decorator