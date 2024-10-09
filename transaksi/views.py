from django.shortcuts import render, redirect, get_object_or_404
from transaksi.forms import TransaksiKeluarForm, DendaForm
from transaksi.models import Transaksi
from users.models import User
from django.db.models import Sum
from membership.models import Membership
from users.decorators import role_required
from django.contrib import messages
from datetime import timedelta
from django.utils.dateparse import parse_date
from trainer.models import TrainerSession
@role_required(['Kasir'])
def TransaksiKeluar(request):
    if request.method == 'POST':
        form = TransaksiKeluarForm(request.POST)
        if form.is_valid():
            transaksi = form.save(commit=False)
            transaksi.invoice = Transaksi.generate_invoice_number()
            transaksi.user = request.user
            transaksi.jenis = 'Keluar'
            transaksi.status = 'Berhasil'
            transaksi.save()
            messages.success(request, "Transaksi keluar berhasil ditambahkan")
            return redirect('Dashboard') 
    else:
        form = TransaksiKeluarForm()
    return render(request, 'dashboard.html', {'form': form})
@role_required(['Kasir'])
def DendaMasuk(request):
    if request.method == 'POST':
        form = DendaForm(request.POST)
        if form.is_valid():
            transaksi = form.save(commit=False)
            transaksi.user = request.user
            transaksi.jenis = 'Masuk'
            transaksi.status = 'Berhasil'
            transaksi.invoice = Transaksi.generate_invoice_number()
            transaksi.save()
            messages.success(request, "Transaksi denda berhasil ditambahkan")
            return redirect('Dashboard')
    else:
        form = DendaForm()
    return render(request, 'dashboard.html', {'form': form})
@role_required(['Kasir'])
def batalkanTransaksi(request):
    invoice = request.POST.get('invoice')
    keterangan = request.POST.get('keterangan')
    if not keterangan or not invoice:
            messages.error(request, "Semua kolom harus diisi.")
            return redirect('Dashboard')
    transaksi = get_object_or_404(Transaksi, invoice=invoice)
    if transaksi.status != 'Batal':
        transaksi.status = 'Batal'
        transaksi.keterangan = keterangan
        transaksi.save()
        if transaksi.kategori == 'Membership':
            username = transaksi.nama.split('(')[-1].rstrip(')')
            user = get_object_or_404(User, username=username)
            membership = Membership.objects.filter(user=user).first()
            if membership:
                membership.delete()
        if transaksi.kategori == 'Trainer':
            username = transaksi.nama.split('(')[-1].rstrip(')')
            user = get_object_or_404(User, username=username)
            trainer = TrainerSession.objects.filter(user=user).first()
            if trainer:
                trainer.delete()
        messages.success(request, 'Transaksi berhasil dibatalkan.')
    else:
        messages.warning(request, 'Transaksi sudah dibatalkan sebelumnya.')
    return redirect('Dashboard')
@role_required(['Kasir', 'Admin'])
def RiwayatTransaksi(request):
    transaksi_list = Transaksi.objects.select_related('user')
    
    tanggal_awal = request.GET.get('tanggal_awal')
    tanggal_akhir = request.GET.get('tanggal_akhir')
    kategori = request.GET.get('kategori')
    jenis = request.GET.get('jenis')
    status = request.GET.get('status')
    
    if tanggal_awal and tanggal_akhir:
        awal = parse_date(tanggal_awal)
        akhir = parse_date(tanggal_akhir) + timedelta(days=1) - timedelta(seconds=1)
        transaksi_list = transaksi_list.filter(tanggal_transaksi__range=[awal, akhir])
    
    if kategori:
        transaksi_list = transaksi_list.filter(kategori=kategori)
    
    if jenis:
        transaksi_list = transaksi_list.filter(jenis=jenis)
    
    if status:
        transaksi_list = transaksi_list.filter(status=status)
    
    pendapatan = transaksi_list.filter(jenis='Masuk').aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    pengeluaran = transaksi_list.filter(jenis='Keluar').aggregate(Sum('jumlah'))['jumlah__sum'] or 0
    context = {
        'title': 'Riwayat Transaksi',
        'transaksi_list': transaksi_list,
        'tanggal_awal': tanggal_awal,
        'tanggal_akhir': tanggal_akhir,
        'kategori': kategori,
        'jenis': jenis,
        'status': status,
        'pendapatan': pendapatan,
        'pengeluaran': pengeluaran,
    }
    
    return render(request, 'RiwayatTransaksi.html', context)