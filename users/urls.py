from django.urls import path
from users.views import LoginView, Logout, Dashboard, Karyawan, UpdateKaryawan, tambahKaryawan, Porfile, UpdatePassword, UpdateProfile
urlpatterns = [
    path('', LoginView, name='login'),
    path('dashboard/', Dashboard, name='Dashboard'),
    path('porfile/', Porfile, name='Porfile'),
    path('porfile/update-password', UpdatePassword, name='UpdatePassword'),
    path('porfile/update-profile', UpdateProfile, name='UpdateProfile'),
    path('karyawan/', Karyawan, name='Karyawan'),
    path('karyawan/update/<int:karyawan_id>/', UpdateKaryawan, name='UpdateKaryawan'),
    path('karyawan/tambah/', tambahKaryawan, name='tambahKaryawan'),
    path('logout/', Logout, name='Logout'),
]
