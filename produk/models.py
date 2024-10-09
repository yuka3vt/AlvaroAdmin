from django.db import models

class Produk(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ('Membership', 'Membership'),
        ('Trainer', 'Trainer'),
    )
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField()
    tipe = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES)
    durasi_hari = models.IntegerField()
    harga = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return self.nama
