from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with initial User data'
    def handle(self, *args, **kwargs):
        users_data = [
            {
                "username": "admin",
                "email": "admin@mail.com",
                "password": "AGM32323",
                "nama": "Admin User",
                "gender": "Laki-Laki",
                "telepon": "081234567890",
                "role": "Admin"
            },
        ]

        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    nama=user_data['nama'],
                    gender=user_data['gender'],
                    telepon=user_data['telepon'],
                    role=user_data['role']
                )
                self.stdout.write(self.style.SUCCESS(f"User {user_data['username']} created"))
            else:
                self.stdout.write(self.style.WARNING(f"User {user_data['username']} already exists"))