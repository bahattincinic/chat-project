from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        print extra_fields
        username = extra_fields.get("username")
        password = extra_fields.get("password")
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username, is_active=True)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, *args, **extra_fields):
        return self.create_user(*args, **extra_fields)
