from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
import simplejson

from account.models import User
from chat.models import ChatSession, AnonUser, ChatMessage
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

    def test_get_unauthorized_session_details(self):
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
        data = res.data
        self.assertTrue(data.get('uuid'), session.uuid)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_open_session_to_self(self):
        balkan = User.objects.create(username='balkan')
        balkan.set_password('1q2w3e')
        balkan.save()
        # get session
        url = reverse('session', args=(balkan.username,))
        # login as balkan
        self.assertTrue(self.session_login_as(balkan.username, '1q2w3e'))
        res = self.c.post(path=url, content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_message_to_target_from_anon(self):
        self.test_create_chat_session()
        balkan = User.objects.get(username='balkan')
        balkan.set_password('1q2w3e')
        balkan.save()
        session = ChatSession.objects.get()
        url = reverse('session-messages', args=(balkan.username, session.uuid))
        res = self.c.post(path=url, content_type='application/json',
                          data=simplejson.dumps({'content': 'text message'}))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ChatMessage.objects.count(), 1)
        message = ChatMessage.objects.get()
        self.assertEquals(message.direction, ChatMessage.TO_USER)

    def test_message_to_anon_from_user(self):
        self.test_message_to_target_from_anon()
        content = 'reply message'
        session = ChatSession.objects.get()
        balkan = User.objects.get(username='balkan')
        # login as balkan
        self.assertTrue(self.session_login_as('balkan', '1q2w3e'))
        url = reverse('session-messages', args=(balkan.username, session.uuid))
        res = self.c.post(path=url, content_type='application/json',
                          data=simplejson.dumps({'content': content}))
        self.assertTrue(res.status_code, status.HTTP_201_CREATED)
        session = ChatSession.objects.get()
        self.assertEquals(session.message_set.count(), 2)
        self.assertEquals(ChatMessage.objects.count(), 2)
        new_message = ChatMessage.objects.order_by('-created_at')[0]
        self.assertEquals(new_message.direction, ChatMessage.TO_ANON)
        self.assertEquals(new_message.content, content)
