from django.db import models
from users.models import User
from produk.models import Produk
STATUS = (('Proses', 'Proses'),('Selesai', 'Selesai'),)
class TrainerSession(models.Model):
    user = models.ForeignKey(User, related_name='trainer_sessions', on_delete=models.CASCADE)
    coach = models.ForeignKey(User, related_name='coached_sessions', on_delete=models.CASCADE)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    jumlah_sesi = models.IntegerField()
    status = models.CharField(max_length=8, choices=STATUS, default='Proses')
    def __str__(self):
        return f"{self.user.username} - {self.coach.nama} - {self.produk.nama}"
class TrainingSchedule(models.Model):
    trainer_session = models.ForeignKey(TrainerSession, related_name='schedules', on_delete=models.CASCADE)
    nama = models.CharField(max_length=100)
    mulai = models.DateTimeField()
    selesai = models.DateTimeField()
    deskripsi = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.trainer_session.coach.username} - {self.mulai} - {self.selesai}"