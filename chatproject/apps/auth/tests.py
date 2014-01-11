import simplejson
import uuid
from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from core.tests import CommonTest
from account.models import User


class AuthenticationTestCase(CommonTest, TestCase):

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

    def test_token_invalid_user_login(self):
        """
        user name or password is invalid
        """
        url = reverse('login-token')
        payload = simplejson.dumps({'username': 'invalid',
                                    'password': 'invalid'})
        request = self.c.post(path=url, data=payload,
                              content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_session_invalid_user_login(self):
        """
        user name or password is invalid
        """
        url = reverse('login-session')
        payload = simplejson.dumps({'username': 'invalid',
                                    'password': 'invalid'})
        request = self.c.post(path=url, data=payload,
                              content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

    def test_session_logout(self):
        """
        Session Logout
        """
        url = reverse('logout-session')
        # session login
        self.session_login()
        request = self.c.get(path=url, content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_token_logout(self):
        """
        Token Logout
        """
        # Token Login
        self.token_login()
        url = reverse('logout-token')
        request = self.c.get(path=url,  **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_account_register(self):
        """
        User Register
        """
        url = reverse('user-account-create')
        payload = simplejson.dumps({'username': 'testaccount',
                                    'password': '123456'})
        request = self.c.post(path=url, data=payload,
                              content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        # created
        user = User.objects.filter(username='testaccount')
        self.assertEqual(True, user.exists())

    def test_account_already_username_register(self):
        """
        user name is already in use
        """
        url = reverse('user-account-create')
        payload = simplejson.dumps({'username': self.username,
                                    'password': '123456'})
        request = self.c.post(path=url, data=payload,
                              content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        # not created
        user = User.objects.filter(username='testaccount')
        self.assertNotEqual(True, user.exists())

    def test_account_already_email_register(self):
        """
        email is already in use
        """
        url = reverse('user-account-create')
        payload = simplejson.dumps({'username': 'hed1e32',
                                    'password': '123456',
                                    'email': self.email})
        request = self.c.post(path=url, data=payload,
                              content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        # not created
        user = User.objects.filter(username='hed1e32')
        self.assertNotEqual(True, user.exists())

    def test_account_empty_username_register(self):
        """
        username can not be empty
        """
        url = reverse('user-account-create')
        payload = simplejson.dumps({'password': '123456'})
        request = self.c.post(path=url, data=payload,
                              content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)


class UserForgotTestCase(CommonTest, TestCase):

    def test_forgot_my_password(self):
        """
        Forgot my password
        """
        url = reverse('forgot-password')
        payload = simplejson.dumps({'email': self.email})
        request = self.c.put(path=url, data=payload,
                             content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_forgot_username(self):
        """
        Forgot Username
        """
        url = reverse('forgot-username')
        payload = simplejson.dumps({'email': self.email})
        request = self.c.put(path=url, data=payload,
                             content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_forgot_password_email_invalid(self):
        """
        email invalid
        """
        url = reverse('forgot-password')
        payload = simplejson.dumps({'email': 'ffdf@fdf.com'})
        request = self.c.put(path=url, data=payload,
                             content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_password(self):
        """
        Set New Password
        """
        user = User.objects.filter()[0]
        user.secret_key = uuid.uuid4()
        user.save()
        url = reverse('forgot-new-password')
        payload = simplejson.dumps({
            'email': user.email, 'secret_key': '%s' % user.secret_key,
            'new_password': '123456'
        })
        request = self.c.put(path=url, data=payload,
                             content_type='application/json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        # control
        new_user = User.objects.get(id=user.id)
        self.assertEqual('', new_user.secret_key)
        self.assertEqual(True, new_user.check_password('123456'))
        self.assertNotEquals(user.password, new_user.password)