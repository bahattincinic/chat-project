import re
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

# Username valitors
username_re = re.compile(r'^[A-Za-z0-9-_]{4,25}$')
validate_username = RegexValidator(
    username_re, _('Enter a valid username.'), 'invalid')