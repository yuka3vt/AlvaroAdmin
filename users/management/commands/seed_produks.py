from django.core.management.base import BaseCommand
from produk.models import Produk

class Command(BaseCommand):
    help = 'Seed the database with initial Produk data'

    def handle(self, *args, **kwargs):
        produk_data = [
            {
                "nama": "Daily Membership",
                "deskripsi": "Membership harian untuk akses ke semua fasilitas gym.",
                "tipe": "Membership",
                "durasi_hari": 1,
                "harga": 20000,
            },
            {
                "nama": "Monthly Membership",
                "deskripsi": "Membership bulanan untuk akses ke semua fasilitas gym.",
                "tipe": "Membership",
                "durasi_hari": 30,
                "harga": 100000,
            },
            {
                "nama": "3-Month Membership",
                "deskripsi": "Membership 3 bulan untuk akses ke semua fasilitas gym.",
                "tipe": "Membership",
                "durasi_hari": 90,
                "harga": 300000,
            },
            {
                "nama": "Personal Trainer - 8 Sessions",
                "deskripsi": "Sesi dengan personal trainer untuk 8 pertemuan.",
                "tipe": "Trainer",
                "durasi_hari": 8,
                "harga": 1200000,
            },
            {
                "nama": "Group Trainer - 8 Sessions",
                "deskripsi": "Sesi grup dengan trainer untuk 8 pertemuan.",
                "tipe": "Trainer",
                "durasi_hari": 8,
                "harga": 800000,
            },
            {
                "nama": "Personal Trainer - 12 Sessions",
                "deskripsi": "Sesi dengan personal trainer untuk 12 pertemuan.",
                "tipe": "Trainer",
                "durasi_hari": 12,
                "harga": 1500000,
            },
            {
                "nama": "Group Trainer - 12 Sessions",
                "deskripsi": "Sesi grup dengan trainer untuk 12 pertemuan.",
                "tipe": "Trainer",
                "durasi_hari": 12,
                "harga": 1200000,
            },
        ]

        for produk in produk_data:
            if not Produk.objects.filter(nama=produk['nama']).exists():
                Produk.objects.create(
                    nama=produk['nama'],
                    deskripsi=produk['deskripsi'],
                    tipe=produk['tipe'],
                    durasi_hari=produk['durasi_hari'],
                    harga=produk['harga']
                )
                self.stdout.write(self.style.SUCCESS(f"Produk {produk['nama']} created"))
            else:
                self.stdout.write(self.style.WARNING(f"Produk {produk['nama']} already exists"))
