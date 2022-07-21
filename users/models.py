from typing import List
from django.db import models
from django.contrib.auth.models import AbstractUser


# create a custom User class that extends AbstractUser to ensure model scalability in the future
class User(AbstractUser):
    role: str = models.CharField(max_length=10, choices=[('student', 'student'), ('librarian', 'librarian')], default='student')