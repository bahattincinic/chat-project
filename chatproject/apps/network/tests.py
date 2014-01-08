from rest_framework.status import is_success
import simplejson

from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from core.tests import CommonTest
from account.models import User
from .models import Network, NetworkConnection, NetworkAdmin


class NetworkTestCase(CommonTest, TestCase):
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
        self.assertTrue(isinstance(self.u, User))
        request = self.c.post(path=create_url, data=create_payload,
                              content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        # test what we created
        network = Network.objects.get(name=network_name)
        self.assertTrue(network.is_public)
        self.assertFalse(network.is_deleted)
        self.assertIsNotNone(network.slug)
        self.assertEqual(network.created_by, self.u)
        self.assertEqual(NetworkConnection.objects.count(), 1)
        self.assertEqual(NetworkAdmin.objects.count(), 1)
        admin = NetworkAdmin.objects.get()
        self.assertEqual(admin.user.id, self.u.id)
        self.assertEqual(admin.network.id, network.id)
        self.assertEqual(admin.status, NetworkAdmin.ADMIN)
        connection = NetworkConnection.objects.get()
        self.assertEqual(connection.id, admin.connection.id)


    def test_retrieve_network_details(self):
        self.test_network_create()
        self.assertEqual(Network.objects.count(), 1)
        network = Network.objects.get()
        url = reverse('network-detail', args=(network.slug,))
        response = self.c.get(path=url, content_type='application/json')
        self.assertTrue(is_success(response.status_code))

    def test_network_delete(self):
        self.test_retrieve_network_details()
        network = Network.objects.get()
        self.assertTrue(network.check_ownership(self.u))
        url = reverse('network-detail', args=(network.slug,))
        response = self.c.delete(path=url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_network_update_byid_fail(self):
        self.session_login()
        create_url = reverse('network-lists')
        self.test_network_create()
        self.assertEqual(1, Network.objects.all().count())
        # create by id is not supported
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

    def test_network_connection_creation(self):
        self.session_login()
        self.test_network_create()
        network = Network.objects.get()
        url = reverse('network-users', args=(network.slug,))
        # this expected to fail since self.u
        # has already a connection to this network
        response = self.c.post(path=url, data={},
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # make sure connection count has not changed
        self.assertEqual(NetworkConnection.objects.count(), 1)
        self.assertEqual(NetworkAdmin.objects.all().count(), 1)
        self.session_logout()
        # create a new user for this action
        username = 'osman'
        password = '1q2w3e'
        osman = User.objects.create(username=username)
        osman.set_password(password)
        osman.save()
        self.session_login_as(username, password)
        # now add osman to network
        res = self.c.post(path=url, data={},
                          content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NetworkConnection.objects.count(), 2)
        # get connection of osman
        conn = NetworkConnection.objects.get(user=osman)
        # since network is public connection must be approved immediately
        self.assertTrue(conn.is_approved)
        # osman is not admin
        self.assertEqual(NetworkAdmin.objects.all().count(), 1)
        self.session_logout()

    def test_network_connection_get_delete(self):
        self.test_network_connection_creation()
        self.session_logout()
        self.session_login_as('osman', '1q2w3e')
        network = Network.objects.get()
        osman = User.objects.get(username='osman')
        url = reverse('network-users-detail', args=(network.slug, osman.username))
        # should answer to get with 200
        res = self.c.get(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data
        network = Network.objects.get()
        self.assertEqual(network.id, data.get('network'))
        self.assertEqual(osman.id, data.get('user'))
        # should be 2 conn
        self.assertEqual(NetworkConnection.approved.count(), 2)
        res = self.c.delete(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(NetworkConnection.approved.count(), 1)
        self.assertFalse(NetworkConnection.objects.filter(
            user=osman, network=network).exists())


    def test_network_connection_deletion_admin(self):
        self.test_network_connection_creation()
        self.session_login()
        network = Network.objects.get()
        url = reverse('network-users', args=(network.slug,))

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

