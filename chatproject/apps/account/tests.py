import simplejson

from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from core.tests import CommonTest
from account.models import User, Follow, Report
from account.serializers import UserDetailSerializer


class UserAccountTestCase(CommonTest, TestCase):

    def test_account_detail(self):
        """
        User Account Detail
        """
        url = reverse('user-account-detail', args=[self.username])
        self.token_login()
        request = self.c.get(path=url, content_type='application/json',
                             **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_invalid_account_detail(self):
        """
        Username invalid
        """
        url = reverse('user-account-detail', args=['hededsfd'])
        self.token_login()
        request = self.c.get(path=url, content_type='application/json',
                             **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)

    def test_account_delete(self):
        """
        User Account Delete
        """
        url = reverse('user-account-detail', args=[self.username])
        self.token_login()
        request = self.c.delete(path=url, content_type='application/json',
                                **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_account_delete(self):
        """
        You can only delete itself
        """
        user = User.objects.create_user(username='hede', password='hede')
        url = reverse('user-account-detail', args=[user.username])
        self.token_login()
        request = self.c.delete(path=url, content_type='application/json',
                                **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

    def test_account_update(self):
        """
        User Account Update
        """
        url = reverse('user-account-detail', args=[self.username])
        self.token_login()
        data = UserDetailSerializer(instance=self.u).data
        data['gender'] = User.MALE
        data.pop('background')
        data.pop('avatar')
        request = self.c.put(path=url, data=simplejson.dumps(data),
                             content_type='application/json',
                             **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(data['gender'],
                         User.objects.get(username=self.username).gender)

    def test_account_password_update(self):
        """
        User Account Password Update
        """
        url = reverse('user-change-password', args=[self.username])
        self.token_login()
        data = {'password': self.password, 'new_password': 'testtest',
                'confirm_password': 'testtest'}
        request = self.c.patch(url, data=simplejson.dumps(data),
                               content_type='application/json',
                               **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        # password control
        new_user = User.objects.get(username=self.username)
        self.assertNotEqual(self.u.password, new_user.password)


class UserFollowTestCase(CommonTest, TestCase):

    def test_account_self_follow(self):
        """
        user himself cannot follow
        """
        url = reverse('user-account-follow', args=[self.username])
        self.token_login()
        request = self.c.post(path=url, content_type='application/json',
                              **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

    def test_account_self_unfollow(self):
        """
        user himself cannot unfollow
        """
        url = reverse('user-account-follow', args=(self.u.username,))
        self.token_login()
        request = self.c.delete(path=url, content_type='application/json',
                                **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

    def test_account_follow(self):
        """
        User Follow
        """
        User.objects.get_or_create(username='hede')
        url = reverse('user-account-follow', args=('hede',))
        self.token_login()
        request = self.c.post(path=url, content_type='application/json',
                              **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

    def test_account_invalid_user_follow(self):
        """
        Invalid user can not be follow
        """
        url = reverse('user-account-follow', args=('invalid_user',))
        self.token_login()
        request = self.c.post(path=url, content_type='application/json',
                              **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)

    def test_account_invalid_user_unfollow(self):
        """
        Invalid user can not be unfollow
        """
        url = reverse('user-account-follow', args=('invalid_user',))
        self.token_login()
        request = self.c.delete(path=url, content_type='application/json',
                                **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)

    def test_account_unfollow(self):
        """
        User unfollow
        """
        hede, _ = User.objects.get_or_create(username='hede')
        Follow.objects.create(followee=hede, follower=self.u)
        url = reverse('user-account-follow', args=('hede',))
        self.token_login()
        request = self.c.delete(path=url, content_type='application/json',
                                **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)

    def test_account_followers(self):
        """
        User Followers
        """
        hede = User.objects.create_user(username='hede', password='hede')
        Follow.objects.create(follower=hede, followee=self.u)
        url = reverse('user-account-followers', args=[self.u.username])
        self.token_login()
        request = self.c.get(path=url, content_type='application/json',
                             **self.client_header)
        data = simplejson.loads(request.content)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data.get("results")),
                         Follow.objects.filter(followee=self.u).count())

    def test_account_followees(self):
        """
        User Followees
        """
        user = User.objects.create_user(username='hede', password='hede')
        Follow.objects.create(follower=self.u, followee=user)
        url = reverse('user-account-followees', args=[self.u.username])
        self.token_login()
        request = self.c.get(path=url, content_type='application/json',
                             **self.client_header)
        data = simplejson.loads(request.content)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data.get("results")),
                         Follow.objects.filter(follower=self.u).count())


class UserReportTestCase(CommonTest, TestCase):

    def test_report_create(self):
        """
        Create Report
        """
        user = User.objects.create_user(username='hede', password='hede')
        url = reverse('user-reports', args=[user.username])
        self.token_login()
        data = simplejson.dumps({'text': 'Test'})
        request = self.c.post(path=url, content_type='application/json',
                              data=data, **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

    def test_invalid_user_create_report(self):
        """
        invalid user Create Report
        """
        url = reverse('user-reports', args=['invalid_user'])
        self.token_login()
        data = simplejson.dumps({'text': 'Test'})
        request = self.c.post(path=url, content_type='application/json',
                              data=data, **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_404_NOT_FOUND)

    def test_report_list(self):
        """
        Report List
        """
        user = User.objects.create_user(username='hede', password='hede')
        url = reverse('user-reports', args=[self.u.username])
        self.token_login()
        Report.objects.create(reporter=user, offender=self.u, text='tests',
                              status=Report.ACTIVE)
        request = self.c.get(path=url, content_type='application/json',
                             **self.client_header)
        data = simplejson.loads(request.content)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data.get("results")),
                         Report.objects.filter(offender=self.u).count())

    def test_other_user_report_list(self):
        """
        Other User Reports List
        """
        user = User.objects.create_user(username='hede', password='hede')
        url = reverse('user-reports', args=[user.username])
        self.token_login()
        request = self.c.get(path=url, content_type='application/json',
                             **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

    def test_report_detail(self):
        """
        Report Detail
        """
        user = User.objects.create_user(username='hede', password='hede')
        self.token_login()
        report = Report.objects.create(reporter=user, offender=self.u,
                                       text='tests', status=Report.ACTIVE)
        url = reverse('user-report-detail', args=[self.u.username, report.id])
        request = self.c.get(path=url, **self.client_header)
        self.assertEqual(request.status_code, status.HTTP_200_OK)