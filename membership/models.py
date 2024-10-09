from django.db import models
from users.models import User
from produk.models import Produk
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    tanggal_mulai = models.DateField()
    tanggal_akhir = models.DateField()
    def __str__(self):
        return f"{self.user.nama} - {self.produk.nama}"