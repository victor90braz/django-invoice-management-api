# In InvoicesAccounting/app/models/user_model.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserModel(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    # Fixing the clashes by adding unique related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='invoicesaccounting_user_set',  # Custom related name
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='invoicesaccounting_user_permissions_set',  # Custom related name
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )

    def __str__(self):
        return self.username
