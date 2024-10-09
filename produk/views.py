from django.shortcuts import render, get_object_or_404, redirect
from users.decorators import role_required
from produk.models import Produk
from produk.forms import ProdukForm
from django.contrib import messages
from django.urls import reverse
@role_required(['Admin'])
def ProdukIndex(request):
    produks = Produk.objects.all()
    tipe = request.GET.get('tipe')
    if tipe:
        produks = produks.filter(tipe=tipe)
    context = {
        'title' : 'Paket Produk',
        'produks': produks,
        'tipe' : tipe
    }
    return render(request, 'produk/ProdukIndex.html', context)
@role_required(['Admin'])
def TambahProduk(request):
    if request.method == 'POST':
        form = ProdukForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, f'Produk berhasil ditambahkan.')
            return redirect('ProdukIndex')
        else:
            messages.error(request, 'Gagal menambahkan produk. Silakan periksa form dan coba lagi.')
    else:
        form = ProdukForm()
    context = {
        'title' : 'Paket Produk',
        'form': form
    }
    return render(request, 'produk/ProdukTambah.html', context)
@role_required(['Admin'])
def HapusProduk(request, produk_id):
    produk = get_object_or_404(Produk, id=produk_id)
    produk.delete()
    messages.success(request, f'Produk berhasil dihapus.')
    return redirect(reverse('ProdukIndex'))
@role_required(['Admin'])
def ProdukEdit(request, produk_id):
    produk = get_object_or_404(Produk, id=produk_id)
    if request.method == 'POST':
        form = ProdukForm(request.POST, instance=produk)
        if form.is_valid():
            produk = form.save()
            messages.success(request, f'Produk berhasil diperbarui.')
            return redirect('ProdukIndex')
        else:
            messages.error(request, 'Gagal memperbarui produk. Silakan periksa form dan coba lagi.')
    else:
        form = ProdukForm(instance=produk)
    context = {
        'title' : 'Paket Produk',
        'form': form,
        'produk': produk
    }
    return render(request, 'produk/ProdukEdit.html', context)