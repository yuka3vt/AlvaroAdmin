from django.urls import path
from transaksi.views import TransaksiKeluar, DendaMasuk, batalkanTransaksi, RiwayatTransaksi
urlpatterns = [
    path('keluar/', TransaksiKeluar, name='TransaksiKeluar'),
    path('denda/', DendaMasuk, name='DendaMasuk'),
    path('batal/', batalkanTransaksi, name='batalkanTransaksi'), 
    path('riwayat/', RiwayatTransaksi, name='RiwayatTransaksi'), 
]
