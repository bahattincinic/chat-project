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
        self.assertTrue(self.session_login())
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
        self.assertTrue(self.session_login())
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
        self.assertTrue(self.session_login())
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
        self.assertTrue(self.session_login())
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
        self.assertTrue(self.session_login_as(username, password))
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
        self.assertTrue(self.session_login_as('osman', '1q2w3e'))
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
        self.assertTrue(self.session_login())
        network = Network.objects.get()
        url = reverse('network-users', args=(network.slug,))

    def test_unauthorized_network_creation(self):
        create_url = reverse('network-lists')
        network_name = 'Metro Last Light'
        create_payload = simplejson.dumps({'name': network_name})
        request = self.c.post(path=create_url, data=create_payload,
                              content_type='application/json')
        self.assertFalse(is_success(request.status_code))

    def test_network_add_mod(self):
        self.test_network_connection_creation()
        self.assertEqual(NetworkConnection.approved.count(), 2)
        network = Network.objects.get()
        osman = User.actives.get(username='osman')
        url = reverse('network-mods', args=(network.slug, ))
        # get all mods for this network
        res = self.c.get(path=url, content_type='application/json')
        data = res.data
        # no mods by default, only admin
        self.assertEqual(data['count'], 1)
        self.assertEqual(len(data['results']), 1)
        # appoint osman as mod
        self.assertTrue(self.session_login())
        res = self.c.post(path=url,
                          data=simplejson.dumps({'user': osman.id}),
                          content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NetworkAdmin.objects.count(), 2)
        self.assertEqual(NetworkConnection.approved.count(), 2)
        # only one admin exists
        self.assertEqual(NetworkAdmin.objects.filter(status=NetworkAdmin.ADMIN).count(), 1)
        # only one mode exists
        self.assertEqual(NetworkAdmin.objects.filter(status=NetworkAdmin.MODERATOR).count(), 1)
        mod = NetworkAdmin.objects.get(status=NetworkAdmin.MODERATOR)
        adm = NetworkAdmin.objects.get(status=NetworkAdmin.ADMIN)
        self.assertEqual(mod.user.id, osman.id)
        self.assertEqual(adm.user.id, self.u.id)
        self.session_logout()

    def test_network_delete_mod_as_admin(self):
        self.test_network_add_mod()
        network = Network.objects.get()
        self.assertEqual(NetworkConnection.objects.count(), 2)
        self.assertEqual(NetworkAdmin.objects.count(), 2)
        osman = User.actives.get(username='osman')
        url = reverse('network-mods-detail', args=(network.slug, osman.username))
        self.assertTrue(self.session_login())
        res = self.c.delete(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(NetworkAdmin.objects.count(), 1)
        # no moderator left
        self.assertFalse(NetworkAdmin.objects.filter(
            status=NetworkAdmin.MODERATOR).exists())
        self.assertEqual(NetworkConnection.approved.count(), 2)

    def test_network_delete_mod_as_himself(self):
        self.test_network_add_mod()
        network = Network.objects.get()
        self.assertEqual(NetworkConnection.objects.count(), 2)
        self.assertEqual(NetworkAdmin.objects.count(), 2)
        osman = User.actives.get(username='osman')
        url = reverse('network-mods-detail', args=(network.slug, osman.username))
        self.assertTrue(self.session_login_as('osman', '1q2w3e'))
        res = self.c.delete(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(NetworkAdmin.objects.count(), 1)
        # no moderator left
        self.assertFalse(NetworkAdmin.objects.filter(
            status=NetworkAdmin.MODERATOR).exists())
        self.assertEqual(NetworkConnection.approved.count(), 2)

    def test_network_delete_mod_fail_no_login(self):
        self.test_network_add_mod()
        network = Network.objects.get()
        self.assertEqual(NetworkConnection.objects.count(), 2)
        self.assertEqual(NetworkAdmin.objects.count(), 2)
        osman = User.actives.get(username='osman')
        # no login, try to delete
        url = reverse('network-mods-detail', args=(network.slug, osman.username))
        res = self.c.delete(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(NetworkConnection.approved.count(), 2)
        self.assertEqual(NetworkAdmin.objects.count(), 2)

    def test_network_delete_mod_invalid_login(self):
        self.test_network_delete_mod_fail_no_login()
        network = Network.objects.get()
        osman = User.actives.get(username='osman')
        url = reverse('network-mods-detail', args=(network.slug, osman.username))
        kazim = User.objects.create(username='kazim')
        kazim.set_password('1q2w3e')
        kazim.save()
        # login as kazim
        self.assertTrue(self.session_login_as(kazim.username, '1q2w3e'))
        # no connection to network, try to delete
        res = self.c.delete(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(NetworkConnection.approved.count(), 2)
        self.assertEqual(NetworkAdmin.objects.count(), 2)
        # connect kazim to network
        connect_url = reverse('network-users', args=(network.slug,))
        res = self.c.post(path=connect_url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NetworkConnection.approved.count(), 3)
        self.assertEqual(NetworkAdmin.objects.count(), 2)
        # try to delete osman now
        res = self.c.delete(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(NetworkConnection.approved.count(), 3)
        self.assertEqual(NetworkAdmin.objects.count(), 2)
        # kazim tries to be mod all by himself, expected to fail with 403
        add_mod_url = reverse('network-mods', args=(network.slug, ))
        res = self.c.post(path=add_mod_url,
                          data=simplejson.dumps({'user': kazim.id}),
                          content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(NetworkConnection.approved.count(), 3)
        self.assertEqual(NetworkAdmin.objects.count(), 2)
        # osman tries to make kazim as mod, expected to fail with 403
        self.session_logout()
        self.assertTrue(self.session_login_as('osman', '1q2w3e'))
        res = self.c.post(path=add_mod_url,
                          data=simplejson.dumps({'user': kazim.id}),
                          content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(NetworkConnection.approved.count(), 3)
        self.assertEqual(NetworkAdmin.objects.count(), 2)
        # admin makes kazim a mod
        self.session_logout()


    def test_network_mod_delete(self):
        self.test_network_delete_mod_invalid_login()
        self.assertEqual(NetworkConnection.approved.count(), 3)
        self.assertEqual(NetworkAdmin.objects.count(), 2)
        self.assertTrue(self.session_login())
        network = Network.objects.get()
        add_mod_url = reverse('network-mods', args=(network.slug, ))
        kazim = User.objects.get(username='kazim')
        res = self.c.post(path=add_mod_url,
                          data=simplejson.dumps({'user': kazim.id}),
                          content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NetworkConnection.approved.count(), 3)
        self.assertEqual(NetworkAdmin.objects.count(), 3)

