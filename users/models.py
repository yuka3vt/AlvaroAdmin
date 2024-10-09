from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ('User', 'User'),
    ('Admin', 'Admin'),
    ('Kasir', 'Kasir'),
    ('Coach', 'Coach'),
)
GENDER_CHOICES = (
    ('Laki-Laki', 'Laki-Laki'),
    ('Perempuan', 'Perempuan'),
)
class User(AbstractUser):
    image = models.ImageField(upload_to='profil', blank=True, null=True)
    nama = models.CharField(max_length=50)
    gender = models.CharField(max_length=9, choices=GENDER_CHOICES, default='Laki-Laki')
    telepon = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=5, choices=ROLE_CHOICES, default='User')
    def __str__(self):
        return self.username