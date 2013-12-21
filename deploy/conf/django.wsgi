import os
import sys

root = os.path.join(os.path.dirname(__file__), '/usr/local/src')
sys.path.insert(0, root)
sys.path.append('/opt/projects/{{ project_address }}/src/{{ project_appname }}/{{ project_appname }}')
sys.path.append('/opt/projects/{{ project_address }}/src/{{ project_appname }}/{{ project_appname }}/apps')
os.environ['DJANGO_SETTINGS_MODULE'] = '{{ settings.settings_parent }}.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
