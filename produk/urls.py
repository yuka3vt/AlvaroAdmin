from django.urls import path
from produk.views import ProdukIndex, TambahProduk, HapusProduk, ProdukEdit
urlpatterns = [
    path('', ProdukIndex, name='ProdukIndex'),
    path('tambah/', TambahProduk, name='TambahProduk'),
    path('hapus/<int:produk_id>/', HapusProduk, name='HapusProduk'),
    path('edit/<int:produk_id>/', ProdukEdit, name='ProdukEdit'),
]
