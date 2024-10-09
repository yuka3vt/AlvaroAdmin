from django import forms
from transaksi.models import Transaksi

class TransaksiKeluarForm(forms.ModelForm):
    class Meta:
        model = Transaksi
        fields = ['kategori', 'nama', 'jumlah']
        widgets = {
            'kategori': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nama transaksi'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan jumlah transaksi'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kategori'].initial = 'Operasional'

class DendaForm(forms.ModelForm):
    nama_member = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Member'}))
    nama_denda = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jenis Denda'}))
    class Meta:
        model = Transaksi
        fields = ['kategori', 'jumlah']
        widgets = {
            'kategori': forms.TextInput(attrs={'class': 'form-control', 'readonly': True, 'value': 'Denda'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jumlah Denda'}),
        }
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.nama = f"{self.cleaned_data['nama_member']} - {self.cleaned_data['nama_denda']}"
        if commit:
            instance.save()
        return instance