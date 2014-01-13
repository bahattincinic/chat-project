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
        # now create a session with user
        url = reverse('session', args=(balkan.username,))
        res = self.c.post(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # count check
        self.assertEqual(ChatSession.objects.count(), 1)
        self.assertEqual(AnonUser.objects.count(), 1)
        # get session and created anon user
        self.session = ChatSession.objects.get()
        self.anon = AnonUser.objects.get()
        # checks
        self.assertIsNotNone(self.session.uuid)

    def test_get_unauthorized_session_details(self):
        self.test_create_chat_session()
        balkan = User.objects.get(username='balkan')
        url = reverse('session-detail', args=(balkan.username, self.session.uuid))
        # no login, request session details..
        res = self.c.get(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_session_details(self):
        self.test_create_chat_session()
        self.session_logout()
        # get user and session
        balkan = User.objects.get(username='balkan')
        session = ChatSession.objects.get()
        url = reverse('session-detail', args=(balkan.username, session.uuid))
        print url
        # login as balkan
        self.session_login_as(balkan.username, balkan.password)
        # retrieve session details
        res = self.c.get(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_send_message(self):
        # we created a session with user balkan
        # now send messages with created anon user
        pass
