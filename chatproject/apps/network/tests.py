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

    def login_as_test(self):
        url = reverse('login-session')
        payload = simplejson.dumps({'username': self.username,
                                    'password': self.password})
        request = self.c.post(path=url, data=payload,
                              content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_network_list(self):
        """
        Network List
        """
        url = reverse('network-lists')
        request = self.c.get(path=url,
                             content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_network_create(self):
        """
        Network Create
        """
        self.login_as_test()
        # now create a network
        create_url = reverse('network-lists')
        network_name = 'Metro Last Light'
        create_payload = simplejson.dumps({'name': network_name})
        request = self.c.post(path=create_url, data=create_payload,
                              content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        # test what we created
        network = Network.objects.get(name=network_name)
        self.assertTrue(network.is_public)
        self.assertFalse(network.is_deleted)
        self.assertIsNotNone(network.slug)
        self.assertEqual(network.created_by, self.user)

