from rest_framework.status import is_success
import simplejson

from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from core.tests import CommonTest
from .models import Network
from network.models import NetworkConnection, NetworkAdmin
from account.models import User


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

    def test_network_update_fail(self):
        self.session_login()
        create_url = reverse('network-lists')
        self.test_network_create()
        self.assertEqual(1, Network.objects.all().count())
        total_url = '%s%s/' % (create_url, Network.objects.get().id)
        request = self.c.post(path=total_url,
                              data=simplejson.dumps({'name': 'xxx'}),
                              content_type='application/json')
        # we expect this to fail
        self.assertFalse(is_success(request.status_code))

    def test_network_connection(self):
        self.session_login()
        self.test_network_create()
        # make sure network admin and network connection are created along
        # with network instance
        self.assertEqual(NetworkConnection.objects.all().count(), 1)
        self.assertEqual(NetworkAdmin.objects.all().count(), 1)
        self.assertEqual(NetworkAdmin.objects.get().user.id, User.actives.get().id)
        # delete network, make sure network connection and network admin removed as well
        Network.objects.all().delete()
        self.assertEqual(NetworkAdmin.objects.all().count(), 0)
        self.assertEqual(NetworkConnection.objects.all().count(), 0)

    def test_unauthorized_network_creation(self):
        create_url = reverse('network-lists')
        network_name = 'Metro Last Light'
        create_payload = simplejson.dumps({'name': network_name})
        request = self.c.post(path=create_url, data=create_payload,
                              content_type='application/json')
        self.assertFalse(is_success(request.status_code))

    def test_network_add_admin(self):
        self.session_login()
        self.test_network_create()
        network = Network.objects.get()
        mod_url = reverse('network-mods', args=(network.id,))
        response = self.c.get(path=mod_url,
                              content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data.get('count'), 1)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['user'], self.u.id)
        self.assertEqual(data['results'][0]['network'], network.id)

    def test_network_connection_deletion(self):
        self.session_login()
        self.test_network_create()
        network = Network.objects.get()
        user = self.u
        delete_url = reverse('network-users-detail', args=(network.id, user.id))
        print delete_url

