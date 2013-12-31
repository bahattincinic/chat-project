import simplejson

from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from core.tests import CommonTest
from .models import Network


class NetworkTestCase(CommonTest, TestCase):
    def tearDown(self):
        # purges all previous network data
        Network.objects.all().delete()

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
        self.session_login()
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
        self.assertEqual(network.created_by, self.u)

    def test_network_update(self):
        self.session_login()
        create_url = reverse('network-lists')
        self.assertEqual(0, Network.objects.all().count())

