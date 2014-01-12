import re
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

# uuid valitors
uuid_re_string = '^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab]' \
                 '[a-f0-9]{3}-?[a-f0-9]{12}\Z'
uuid_re = re.compile(uuid_re_string, re.I)
validate_uuid = RegexValidator(uuid_re, _('Enter a valid uuid.'), 'invalid')