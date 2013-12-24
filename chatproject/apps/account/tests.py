import simplejson

from django.test import TestCase
from django.core.urlresolvers import reverse
from .models import User
from django.test.client import Client
from rest_framework import status


class AuthenticationTestCase(TestCase):

    def setUp(self):
        self.username = 'test'
        self.password = 123456
        User.objects.create_user(self.username, self.password)
        self.c = Client()

    def test_token_login(self):
        """
        Token Login
        """
        url = reverse('login-token')
        payload = simplejson.dumps({'username': self.username,
                                    'password': self.password})
        request = self.c.post(path=url, data=payload,
                              content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_session_login(self):
        """
        Session Login
        """
        url = reverse('login-session')
        payload = simplejson.dumps({'username': self.username,
                                    'password': self.password})
        request = self.c.post(path=url, data=payload,
                              content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
