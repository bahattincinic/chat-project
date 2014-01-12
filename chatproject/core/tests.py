import simplejson

from django.test.client import Client
from account.models import User
from django.core.urlresolvers import reverse

# Test User username and password
TEST_USERNAME = 'test'
TEST_PASSWORD = 123456
TEST_EMAIL = 'test@test.com'


class CommonTest(object):
    username = TEST_USERNAME
    password = TEST_PASSWORD
    email = TEST_EMAIL
    c = Client()
    client_header = {}
    u = User.objects.none()

    def setUp(self):
        self.u = User.objects.create_user(self.username, self.password,
                                          email=self.email)

    def session_login(self):
        self.c.login(username=self.username, password=self.password)

    def session_login_as(self, username, password):
        self.c.login(username=username, password=password)

    def session_logout(self):
        self.c.logout()

    def token_login(self):
        url = reverse('login-token')
        payload = simplejson.dumps({'username': self.username,
                                    'password': self.password})
        request = self.c.post(path=url, data=payload,
                              content_type='application/json')
        request_json = simplejson.loads(request.content)
        self.client_header['HTTP_AUTHORIZATION'] = 'Token %s' %(
            request_json.get('token'))

    def token_logout(self):
        self.token_login()
        url = reverse('logout-token')
        self.c.get(path=url,  **self.client_header)