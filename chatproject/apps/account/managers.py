from django.contrib.auth.models import BaseUserManager
from core.managers import ManagerMixins, FilteringMixin


class UserManager(BaseUserManager, ManagerMixins, FilteringMixin):

    def __init__(self, **kwargs):
        self.filtering = kwargs
        super(UserManager, self).__init__()

    def create_user(self, username, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username, is_active=True, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        return self.create_user(username=username, password=password,
                                **extra_fields)