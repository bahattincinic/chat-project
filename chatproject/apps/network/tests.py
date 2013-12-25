import simplejson

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from rest_framework import status
from account.models import User
from .models import Network


class NetworkTestCase(TestCase):

    def setUp(self):
        self.username = 'test'
        self.password = 123456
        self.user = User.objects.create_user(self.username, self.password)
        Network.objects.create(name="Moscow Metro 2033",
                               created_by=self.user)
        self.c = Client()

    def test_network_list(self):
        """
        Network List
        """
        url = reverse('network-lists')
        request = self.c.get(path=url,
                             content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    # def test_session_login(self):
    #     """
    #     Session Login
    #     """
    #     url = reverse('login-session')
    #     payload = simplejson.dumps({'username': self.username,
    #                                 'password': self.password})
    #     request = self.c.post(path=url, data=payload,
    #                           content_type='application/json')
    #     self.assertEqual(request.status_code, status.HTTP_200_OK)
