from django.db import models
from django.contrib.auth.models import AbstractUser


# create a custom User class that extends AbstractUser to ensure model scalability in the future
class User(AbstractUser):
    pass