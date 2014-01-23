from django.conf import settings


def gen(apart, new_m_time):
    project_name = getattr(settings, 'PROJECT_NAME', 'static')
    start = "/%s" % project_name
    new_filename = ''.join([start, '.%s' % new_m_time, apart[1]])
    return new_filename