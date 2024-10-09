from django.urls import path
from trainer.views import TrainerBaru, TrainerIndex, DetailTrainer,TambahJadwal, UpdateJadwal, TambahTrainer, RiwayatTrainer
urlpatterns = [
    path('baru/', TrainerBaru, name='TrainerBaru'),
    path('perpanjang/', TambahTrainer, name='TambahTrainer'),
    path('index/', TrainerIndex, name='TrainerIndex'),
    path('riwayat/', RiwayatTrainer, name='RiwayatTrainer'),
    path('detail/<int:id>/', DetailTrainer, name='DetailTrainer'),
    path('update/jadwal/<int:id>/', UpdateJadwal, name='UpdateJadwal'),
    path('tambah/jadwal/<int:id>/', TambahJadwal, name='TambahJadwal'),
]
