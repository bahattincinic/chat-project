from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status

from account.models import User
from chat.models import ChatSession, AnonUser
from core.tests import CommonTest


class ChatTestCase(CommonTest, TestCase):
    def test_create_chat_session(self):
        # create target user
        balkan = User.objects.create(username='balkan')
        balkan.set_password('1q2w3e')
        balkan.save()
        self.assertTrue(User.actives.filter(username='balkan').exists())
        # now create a session with user
        url = reverse('session', args=(balkan.username,))
        res = self.c.post(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # count check
        self.assertEqual(ChatSession.objects.count(), 1)
        session = ChatSession.objects.get()
        self.assertEqual(AnonUser.objects.count(), 1)
        anon = session.anon
        self.assertFalse(anon.is_registered_user)
        self.assertIsNone(anon.started_by)
        self.assertIsNotNone(anon.username)
        self.assertTrue(anon.username.startswith('anon'))
        # checks
        self.assertIsNotNone(session.uuid)

    def a_test_get_unauthorized_session_details(self):
        self.test_create_chat_session()
        balkan = User.objects.get(username='balkan')
        session = ChatSession.objects.get()
        url = reverse('session-detail', args=(balkan.username, session.uuid))
        # no login, request session details..
        res = self.c.get(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_session_details(self):
        self.test_create_chat_session()
        self.session_logout()
        # login as balkan
        balkan = User.objects.get(username='balkan')
        session = ChatSession.objects.get()
        self.assertTrue(self.session_login_as(balkan.username, '1q2w3e'))
        url = reverse('session-detail', args=(balkan.username, session.uuid))
        # retrieve session details
        res = self.c.get(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_send_message(self):
        # we created a session with user balkan
        # now send messages with created anon user
        pass
