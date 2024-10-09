from django.db import models
from users.models import User
from django.utils import timezone
KATEGORI = (('Denda', 'Denda'),('Trainer', 'Trainer'),('Membership', 'Membership'),('Operasional', 'Operasional'),)
JENIS = (('Keluar', 'Keluar'),('Masuk', 'Masuk'),)
STATUS = (('Berhasil', 'Berhasil'),('Batal', 'Batal'),('Belum Bayar', 'Belum Bayar'),)
class Transaksi(models.Model):
    invoice = models.CharField(max_length=15, unique=True)
    user = models.ForeignKey(User, related_name='transaksi', on_delete=models.CASCADE)
    nama = models.CharField(max_length=50)
    jenis = models.CharField(max_length=7, choices=JENIS)
    kategori = models.CharField(max_length=15, choices=KATEGORI)
    keterangan = models.CharField(max_length=150, blank=True, null=True)
    jumlah = models.DecimalField(max_digits=10, decimal_places=0)
    status = models.CharField(max_length=15, choices=STATUS, default='Belum Bayar')
    tanggal_transaksi = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.nama} - {self.jumlah}"
    @staticmethod
    def generate_invoice_number():
        today = timezone.now().date()
        last_record = Transaksi.objects.order_by('id').last()
        if last_record:
            next_id = last_record.id + 1
        else:
            next_id = 1
        date_str = today.strftime('%d%m%y')
        return f'INV-{date_str}-{next_id}'