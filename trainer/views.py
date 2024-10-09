from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from transaksi.models import Transaksi
from produk.models import Produk
from users.models import User
from datetime import datetime
from trainer.models import TrainerSession, TrainingSchedule
from users.decorators import role_required
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
@role_required(['Admin', 'Kasir', 'Coach'])
def TrainerIndex(request):
    ubahStatus()
    user = request.user
    trainerList = []
    if user.role == "Coach":
        trainerList = TrainerSession.objects.filter(coach_id=user.id, status='Proses').select_related('user', 'produk').prefetch_related('schedules')
        context = { 
            'title': 'Anggota Trainer',
            'trainerList': trainerList,
        }
    if user.role == "Admin":
        trainerList = TrainerSession.objects.filter(status='Proses').select_related('user', 'produk').prefetch_related('schedules').all()
        context = { 
            'title': 'Anggota Trainer',
            'trainerList': trainerList,
        }
    if user.role == "Kasir":
        trainerList = TrainerSession.objects.filter(status='Proses').select_related('user', 'produk').prefetch_related('schedules').all()
        produk_list = Produk.objects.filter(tipe='Trainer')
        coach_list = User.objects.filter(role='Coach') 
        user_list = User.objects.filter(role='User', is_active=True)
        context = { 
            'title': 'Anggota Trainer',
            'trainerList': trainerList,
            'produk_list': produk_list,
            'coach_list': coach_list,
            'user_list': user_list,
        }
    return render(request, 'AnggotaTrainer.html', context)
@role_required(['Kasir'])
def TrainerBaru(request):
    if request.method == 'POST':
        kategori = request.POST.get('kategori')
        produkId = request.POST.get('jenis_session')
        harga = request.POST.get('jumlah')
        coach_id = request.POST.get('coach')
        username = request.POST.get('username')
        telepon = request.POST.get('telepon')
        if not all([kategori, produkId, harga, coach_id, username, telepon]):
            messages.error(request, "Semua kolom harus diisi.")
            return redirect('Dashboard')
        if User.objects.filter(Q(username=username) | Q(telepon=telepon)).exclude(pk=request.user.pk).exists():
            messages.error(request, "Username atau nomor telepon sudah digunakan.")
            return redirect('Dashboard')
        users = User.objects.create_user(
            username=username,
            password='AGM32323',
            role='User',
            telepon=telepon
        )
        jenisTrainer = Produk.objects.get(id=produkId)
        coach = User.objects.get(id=coach_id)
        Transaksi.objects.create(
            invoice=Transaksi.generate_invoice_number(),
            user=request.user,
            nama=f"{jenisTrainer.nama} ({username})",
            jenis='Masuk',
            status='Berhasil',
            kategori=kategori,
            jumlah=harga
        )
        TrainerSession.objects.create(
            user=users,
            coach=coach,
            produk=jenisTrainer,
            jumlah_sesi=jenisTrainer.durasi_hari,
        )
        messages.success(request, "Transaksi trainer berhasil ditambahkan")
        return redirect('Dashboard')
    return redirect('Dashboard')
@role_required(['Kasir'])
def TambahTrainer(request):
    if request.method == 'POST':
        kategori = request.POST.get('kategori')
        produkId = request.POST.get('jenis_session')
        harga = request.POST.get('jumlah')
        coach_id = request.POST.get('coach')
        username = request.POST.get('username')
        telepon = request.POST.get('telepon')
        
        if not all([kategori, produkId, harga, coach_id, username, telepon]):
            messages.error(request, "Semua kolom harus diisi.")
            return redirect('TrainerIndex')
        
        users = User.objects.filter(username=username).exclude(pk=request.user.pk).first()
        if not users:
            messages.error(request, "Username tidak ditemukan")
            return redirect('TrainerIndex')
        if users.telepon != telepon:
            if User.objects.filter(Q(telepon=telepon)).exclude(pk=request.user.pk).exists():
                messages.error(request, "Nomor telepon sudah digunakan.")
                return redirect('TrainerIndex')
            
            users.telepon = telepon
            users.save()

        jenisTrainer = Produk.objects.get(id=produkId)
        coach = User.objects.get(id=coach_id)
        TrainerSession.objects.create(
            user=users,
            coach=coach,
            produk=jenisTrainer,
            jumlah_sesi=jenisTrainer.durasi_hari,
        )
        Transaksi.objects.create(
            invoice=Transaksi.generate_invoice_number(),
            user=request.user,
            nama=f"{jenisTrainer.nama} ({username})",
            jenis='Masuk',
            status='Berhasil',
            kategori=kategori,
            jumlah=harga
        )
        messages.success(request, "Berhasil menambahkan trainer baru")
        return redirect('TrainerIndex')
    return redirect('TrainerIndex')
@role_required(['Coach'])
def DetailTrainer(request, id):
    trainerDetail = get_object_or_404(TrainerSession.objects.filter(coach_id=request.user).select_related('user', 'produk'), id=id)
    jadwalTrainer = trainerDetail.schedules.all().order_by('nama')
    totalJadwal = jadwalTrainer.count()
    labelNama = []
    jumlahSesiRange = range(1, trainerDetail.jumlah_sesi + 1)
    for i in jumlahSesiRange:
        label = f'Pertemuan ke-{i}'
        if jadwalTrainer.filter(nama=label).exists():
            labelNama.append({'nama': label, 'disable': True})
        else:
            labelNama.append({'nama': label, 'disable': False})
            break
    jumlahSelesai = 0
    now = datetime.now()
    jadwalDenganStatus = []
    for schedule in jadwalTrainer:
        jadwal = timezone.localtime(schedule.selesai).replace(tzinfo=None)
        if now > jadwal:
            status = 'Selesai'
            jumlahSelesai += 1
        else:
            status = 'Proses'
        jadwalDenganStatus.append({
            'id': schedule.id,
            'nama': schedule.nama,
            'mulai': schedule.mulai,
            'selesai': schedule.selesai,
            'deskripsi': schedule.deskripsi,
            'status': status
        })
    progresBar = (jumlahSelesai / totalJadwal) * 100 if totalJadwal > 0 else 0
    context = {
        'title': 'Jadwal Trainer',
        'trainerDetail': trainerDetail,
        'labelNama': labelNama,
        'progresBar': progresBar,
        'jadwalDenganStatus': jadwalDenganStatus,
    }
    return render(request, 'DetailTrainer.html', context)
@role_required(['Coach'])
def TambahJadwal(request, id):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        tanggal = request.POST.get('waktu')
        mulai = request.POST.get('mulai')
        selesai = request.POST.get('selesai')
        deskripsi = request.POST.get('deskripsi')
        if not nama or not tanggal or not mulai or not selesai or not deskripsi:
            messages.error(request, "Semua kolom harus diisi.")
            return redirect(reverse('DetailTrainer', args=[id]))
        try:
            tanggal = datetime.strptime(tanggal, '%Y-%m-%d').date()
            mulai = datetime.strptime(mulai, '%H:%M').time()
            selesai = datetime.strptime(selesai, '%H:%M').time()
            waktuMulai = datetime.combine(tanggal, mulai)
            waktuSelesai = datetime.combine(tanggal, selesai)
            waktuMulai = timezone.make_aware(waktuMulai, timezone.get_default_timezone())
            waktuSelesai = timezone.make_aware(waktuSelesai, timezone.get_default_timezone())
        except ValueError:
            messages.error(request, 'Format waktu tidak valid.')
            return redirect(reverse('DetailTrainer', args=[id]))
        now = timezone.now()
        if waktuSelesai <= now:
            messages.error(request, 'Jadwal ditetapkan harus melewati waktu hari ini!')
            return redirect(reverse('DetailTrainer', args=[id]))
        sesiTrainer = get_object_or_404(TrainerSession.objects.filter(coach_id=request.user), id=id)
        jadwalTersedia = sesiTrainer.schedules.order_by('selesai')
        pertemuan_ke = int(nama.split('-')[-1])
        if pertemuan_ke > 1:
            jadwalSebelum = jadwalTersedia.filter(nama=f'Pertemuan ke-{pertemuan_ke - 1}').first()
            if not jadwalSebelum:
                messages.error(request, 'Jadwal sebelumnya belum ditemukan.')
                return redirect(reverse('DetailTrainer', args=[id]))
            if waktuSelesai <= jadwalSebelum.selesai:
                messages.error(request, 'Jadwal ditetapkan harus setelah jadwal (Pertemuan ke-'+ str(pertemuan_ke - 1) +')')
                return redirect(reverse('DetailTrainer', args=[id]))
        trainers = TrainerSession.objects.filter(coach_id=request.user)
        for trainer in trainers:
            jadwals = trainer.schedules.filter(trainer_session=trainer)
            for jadwal in jadwals:
                if jadwal.mulai == waktuMulai and jadwal.selesai == waktuSelesai:
                    messages.error(request, 'Jadwal yang ditambahkan mengalami bentrok')
                    return redirect(reverse('DetailTrainer', args=[id]))
        TrainingSchedule.objects.create(
            trainer_session=sesiTrainer,
            nama=nama,
            mulai=waktuMulai,
            selesai=waktuSelesai,
            deskripsi=deskripsi,
        )
        messages.success(request, 'Jadwal berhasil ditambahkan.')
        return redirect(reverse('DetailTrainer', args=[id]))
    return redirect(reverse('DetailTrainer', args=[id]))
@role_required(['Coach'])
def UpdateJadwal(request, id):
    if request.method == 'POST':
        id_detail = request.POST.get('idDetail')
        nama = request.POST.get('nama')
        tanggal = request.POST.get('waktu')
        mulai = request.POST.get('mulai')
        selesai = request.POST.get('selesai')
        deskripsi = request.POST.get('deskripsi')
        if not nama or not tanggal or not mulai or not selesai or not deskripsi:
            messages.error(request, "Semua kolom harus diisi.")
            return redirect(reverse('DetailTrainer', args=[id_detail]))
        try:
            tanggal = datetime.strptime(tanggal, '%Y-%m-%d').date()
            mulai = datetime.strptime(mulai, '%H:%M').time()
            selesai = datetime.strptime(selesai, '%H:%M').time()
            waktuMulai = datetime.combine(tanggal, mulai)
            waktuSelesai = datetime.combine(tanggal, selesai)
            waktuMulai = timezone.make_aware(waktuMulai, timezone.get_default_timezone())
            waktuSelesai = timezone.make_aware(waktuSelesai, timezone.get_default_timezone())
        except ValueError:
            messages.error(request, 'Format waktu tidak valid.')
            return redirect(reverse('DetailTrainer', args=[id_detail]))
        now = timezone.now()
        if waktuSelesai <= now:
            messages.error(request, 'Jadwal ditetapkan harus melewati waktu hari ini!')
            return redirect(reverse('DetailTrainer', args=[id_detail]))
        sesiTrainer = get_object_or_404(TrainerSession.objects.filter(coach_id=request.user), id=id_detail)
        jadwalTersedia = sesiTrainer.schedules.order_by('selesai')
        pertemuan_ke = int(nama.split('-')[-1])
        if pertemuan_ke > 1:
            jadwalSebelum = jadwalTersedia.filter(nama=f'Pertemuan ke-{pertemuan_ke - 1}').first()
            if not jadwalSebelum:
                messages.error(request, 'Jadwal sebelumnya belum ditemukan.')
                return redirect(reverse('DetailTrainer', args=[id_detail]))
            if waktuSelesai <= jadwalSebelum.selesai:
                messages.error(request, 'Jadwal ditetapkan harus setelah jadwal (Pertemuan ke-'+ str(pertemuan_ke - 1) +')')
                return redirect(reverse('DetailTrainer', args=[id_detail]))
        trainers = TrainerSession.objects.filter(coach_id=request.user)
        for trainer in trainers:
            jadwals = trainer.schedules.filter(trainer_session=trainer)
            for jadwal in jadwals:
                if jadwal.mulai == waktuMulai and jadwal.selesai == waktuSelesai:
                    messages.error(request, 'Jadwal yang ditambahkan mengalami bentrok')
                    return redirect(reverse('DetailTrainer', args=[id_detail]))
        trainerDetail = get_object_or_404(TrainingSchedule, id=id)
        trainerDetail.mulai = waktuMulai
        trainerDetail.selesai = waktuSelesai
        trainerDetail.deskripsi = deskripsi
        trainerDetail.save()
        messages.success(request, 'Jadwal berhasil diperbarui.')
        return redirect(reverse('DetailTrainer', args=[id_detail]))
    return redirect(reverse('DetailTrainer', args=[id_detail]))
def ubahStatus():
    trainerDetail = TrainerSession.objects.filter(status="Proses")
    for trainer in trainerDetail:
        jadwalTrainer = trainer.schedules.all().order_by('nama')
        totalJadwal = jadwalTrainer.count()
        jumlahSelesai = 0
        now = datetime.now()
        if totalJadwal == trainer.jumlah_sesi:
            for schedule in jadwalTrainer:
                jadwal = timezone.localtime(schedule.selesai).replace(tzinfo=None)
                if now > jadwal:
                    jumlahSelesai += 1
            if jumlahSelesai == totalJadwal:
                trainer.status = "Selesai"
                trainer.save()
@role_required(['Coach'])
def RiwayatTrainer(request):
    user = request.user
    trainerList = TrainerSession.objects.filter(coach_id=user.id, status='Selesai').select_related('user', 'produk').prefetch_related('schedules')
    context = { 
        'title': 'Riwayat Trainer',
        'trainerList': trainerList,
    }
    return render(request, 'RiwayatTrainer.html', context)