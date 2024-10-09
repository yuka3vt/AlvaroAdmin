from django import forms
from produk.models import Produk

class ProdukForm(forms.ModelForm):
    class Meta:
        model = Produk
        fields = ['nama', 'durasi_hari', 'tipe', 'deskripsi', 'harga']