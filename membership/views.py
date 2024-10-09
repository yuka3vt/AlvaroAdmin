from users.decorators import role_required
from django.shortcuts import render, redirect
from membership.models import Membership
from django.utils.timezone import now
from django.utils import timezone
from transaksi.models import Transaksi
from users.models import User
from produk.models import Produk
from users.decorators import role_required
from django.contrib import messages
@role_required(['Admin', 'Kasir'])
def MemberDetails(request):
    memberships = Membership.objects.select_related('user', 'produk').all()
    hariIni = now().date() 
    for membership in memberships:
        membership.sisa_hari = (membership.tanggal_akhir - hariIni).days
    membership_list =  Produk.objects.filter(tipe='Membership')
    user_list = User.objects.filter(role='User', is_active=True)
    context = {
        'title' : 'Anggota Membership',
        'memberships': memberships,
        'user_list': user_list,
        'membership_list' : membership_list,
    }
    return render(request, 'AnggotaMember.html', context)
@role_required(['Kasir'])
def MembershipBaru(request):
    if request.method == 'POST':
        kategori = request.POST.get('kategori')
        jenis_membership_id = request.POST.get('jenis_membership')
        jumlah = request.POST.get('jumlah')
        username = request.POST.get('username')
        if not kategori or not jenis_membership_id or not jumlah or not username:
            messages.error(request, "Semua kolom harus diisi.")
            return redirect('Dashboard')
        users = User.objects.filter(username=username).exclude(pk=request.user.pk).first()
        if users:
            messages.error(request, "Username sudah digunakan.")
            return redirect('Dashboard')
        users = User.objects.create_user(username=username,password='AGM32323', role='User')
        membership = Produk.objects.get(id=jenis_membership_id)
        tanggal_mulai = timezone.now().date()
        tanggal_akhir = tanggal_mulai + timezone.timedelta(days=membership.durasi_hari)
        Membership.objects.create(
            user=users,
            produk=membership,
            tanggal_mulai=tanggal_mulai,
            tanggal_akhir=tanggal_akhir
        )
        Transaksi.objects.create(
            invoice=Transaksi.generate_invoice_number(),
            user=request.user,
            nama=f"{membership.nama} ({username})",
            jenis='Masuk',
            status='Berhasil',
            kategori=kategori,
            jumlah=jumlah
        )
        messages.success(request, "Transaksi membership berhasil ditambahkan")
        return redirect('Dashboard')
    return redirect('Dashboard')
@role_required(['Kasir'])
def TambahMembership(request):
    if request.method == 'POST':
        kategori = request.POST.get('kategori')
        jenis_membership_id = request.POST.get('jenis_membership')
        jumlah = request.POST.get('jumlah')
        username = request.POST.get('username')
        if not kategori or not jenis_membership_id or not jumlah or not username:
            messages.error(request, "Semua kolom harus diisi.")
            return redirect('MemberDetails')
        users = User.objects.filter(username=username).exclude(pk=request.user.pk).first()
        if not users:
            messages.error(request, "Username tidak ditemukan")
            return redirect('MemberDetails')
        produk = Produk.objects.get(id=jenis_membership_id)
        tanggal_mulai = timezone.now().date()
        tanggal_akhir = tanggal_mulai + timezone.timedelta(days=produk.durasi_hari)
        membership = Membership.objects.filter(user=users).first()
        if not membership:
            membership = Membership.objects.create(
                user=users,
                produk=produk,
                tanggal_mulai=tanggal_mulai,
                tanggal_akhir=tanggal_akhir
            )
        else:
            membership.produk = produk
            membership.tanggal_mulai = tanggal_mulai
            membership.tanggal_akhir = tanggal_akhir
            membership.save()
        Transaksi.objects.create(
            invoice=Transaksi.generate_invoice_number(),
            user=request.user,
            nama=f"{produk.nama} ({username})",
            jenis='Masuk',
            status='Berhasil',
            kategori=kategori,
            jumlah=jumlah
        )
        messages.success(request, "Berhasil menambahkan memberhsip")
        return redirect('MemberDetails')
    return redirect('MemberDetails')