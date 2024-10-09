from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from trainer.models import TrainerSession,TrainingSchedule
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.utils.timezone import make_aware
from django.db.models import Count, F, Sum
from transaksi.models import Transaksi
from datetime import datetime, timedelta
from membership.models import Membership
from users.decorators import role_required
from django.contrib import messages
from django.utils import timezone
from produk.models import Produk
from django.conf import settings
from users.models import User
import os
@role_required(['Admin', 'Kasir', 'Coach', 'User'])
def Logout(request):
    logout(request)
    return redirect('/')
def LoginView(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user_obj = User.objects.get(username=username)
            if user_obj.role == 'User':
                messages.error(request, "Invalid username or password.")
            else:
                if user_obj.is_active:
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect('Dashboard')
                    else:
                        messages.error(request, "Invalid username or password.")
                else:
                    messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})
@role_required(['Admin', 'Kasir', 'Coach'])
def Dashboard(request):
    user = request.user
    hariIni = timezone.localtime(timezone.now()).date()
    mulai = timezone.make_aware(datetime.combine(hariIni, datetime.min.time()))
    selesai = timezone.make_aware(datetime.combine(hariIni, datetime.max.time()))
    if user.role == "Admin":
        transaksi_list = Transaksi.objects.filter(tanggal_transaksi__range=(mulai, selesai)).filter(status='Berhasil').select_related('user')
        total_pendapatan = transaksi_list.filter(jenis='Masuk').aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        total_pengeluaran = transaksi_list.filter(jenis='Keluar').aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        jumlah_membership_aktif = Membership.objects.filter(tanggal_akhir__gte=hariIni).count()
        jumlah_trainer_proses = TrainerSession.objects.filter(status='Proses').count()
        context = {
            'title' : 'Dashboard',
            'transaksi_list': transaksi_list,
            'jumlah_membership_aktif': jumlah_membership_aktif,
            'jumlah_trainer_proses': jumlah_trainer_proses,
            'total_pendapatan': total_pendapatan,
            'total_pengeluaran': total_pengeluaran
        }
    elif user.role == "Kasir":
        transaksi_list = Transaksi.objects.filter(tanggal_transaksi__range=(mulai, selesai),status='Berhasil').select_related('user')
        membership_list =  Produk.objects.filter(tipe='Membership')
        trainer_list = Produk.objects.filter(tipe='Trainer')
        coach_list = User.objects.filter(role='Coach') 
        user_list = User.objects.filter(role='User', is_active=True)
        context = {
            'title' : 'Dashboard',
            'user_list': user_list,
            'transaksi_list': transaksi_list,
            'membership_list' : membership_list,
            'trainer_list' : trainer_list,
            'coach_list' : coach_list
        }
    elif user.role == "Coach":
        topTrainer = TrainerSession.objects.filter(coach=user) \
            .values('user__username') \
            .annotate(jumlah=Count('user')) \
            .order_by('-jumlah')[:5]
        belumTerjadwal = TrainerSession.objects.annotate(schedule_count=Count('schedules')).filter(schedule_count__lt=F('jumlah_sesi'),coach=user)
        jadwalMingguan = getJadwalMingguan(request.user.id)
        formatJadwal = getFormatJadwal(jadwalMingguan)
        context = {
            'title' : 'Dashboard',
            'topTrainer': topTrainer,
            'belumTerjadwal': belumTerjadwal,
            'jadwal' : formatJadwal,
        }
    else:
        logout(request)
        return redirect('/')
    return render(request, 'dashboard.html', context)
@role_required(['Admin'])
def Karyawan(request):
    userS = User.objects.all()
    context = {
        'title' : 'User',
        'users': userS
    }
    return render(request, 'User.html', context)
@role_required(['Admin'])
def UpdateKaryawan(request, karyawan_id):
    karyawan = get_object_or_404(User, id=karyawan_id)
    if request.method == 'POST':
        is_active = request.POST.get('is_active') == 'on'
        karyawan.is_active = is_active
        karyawan.save()
        messages.success(request, "Data karyawan berhasil diperbarui.")
        return redirect('Karyawan') 
    
    return render(request, 'Karyawan.html', {'karyawan': karyawan})
@role_required(['Admin'])
def tambahKaryawan(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        username = request.POST.get('username')
        gender = request.POST.get('gender')
        role = request.POST.get('role')
        telepon = request.POST.get('telepon')
        email = request.POST.get('email')
        is_active = request.POST.get('is_active') == 'on'
        try:
            user = User.objects.create(
                username=username,
                nama=nama,
                email=email,
                gender=gender,
                role=role,
                telepon=telepon,
                is_active=is_active,
            )
            user.set_password('AGM32323')
            user.save()
            messages.success(request, 'Karyawan berhasil ditambahkan.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('Karyawan')
    return render(request, 'Karyawan.html')
def getJadwalMingguan(coach_id):
    now = datetime.now()
    hariIni = datetime(now.year, now.month, now.day)
    awalMinggu = make_aware(hariIni)
    akhirMinggu = make_aware(hariIni + timedelta(days=7))
    schedules = TrainingSchedule.objects.filter(trainer_session__coach_id=coach_id,mulai__range=(awalMinggu, akhirMinggu)).order_by('mulai')
    return schedules
def getFormatJadwal(jadwals):
    jadwalTrainer = []
    tanggalSebelumnya = None
    jadwalTersedia = None
    for jadwal in jadwals:
        tanggal = jadwal.mulai.date()
        if tanggal != tanggalSebelumnya:
            if jadwalTersedia:
                jadwalTrainer.append(jadwalTersedia)
            tanggalSebelumnya = tanggal
            jadwalTersedia = {
                "jadwal": True,
                "tanggal": tanggal,
                "client": []
            }
        jadwalTersedia["client"].append({
            'id': jadwal.trainer_session_id,
            'nama': jadwal.trainer_session.user.username,
            'nama': jadwal.trainer_session.user.username,
            'jamMulai': jadwal.mulai,
            'jamSelesai': jadwal.selesai
        })
    if jadwalTersedia:
        jadwalTrainer.append(jadwalTersedia)

    hariIni = datetime.now().date()
    tanggalSatuMinggu = {hariIni + timedelta(days=i) for i in range(7)}
    adaJadwal = {entry["tanggal"] for entry in jadwalTrainer}
    jadwalKosong = tanggalSatuMinggu - adaJadwal

    for item in jadwalKosong:
        jadwalTrainer.append({
            "jadwal": False,
            "tanggal": item,
            "client": []
        })

    jadwalTrainer.sort(key=lambda x: x["tanggal"])
    return jadwalTrainer
@role_required(['Admin', 'Kasir', 'Coach'])
def Porfile(request):
    user = request.user
    context = {
        'title' : 'Profile',
        'user': user
    }
    return render(request, 'Profile.html', context)
@role_required(['Admin', 'Kasir', 'Coach'])
def UpdatePassword(request):
    if request.method == 'POST':
        password_lama = request.POST.get('password_lama')
        password = request.POST.get('password')
        ulangi_password = request.POST.get('ulangi_password')
        if not all([password_lama, password, ulangi_password]):
            messages.error(request, "Semua field harus diisi.")
            return redirect('Porfile')
        user = authenticate(username=request.user.username, password=password_lama)
        if user is None:
            messages.error(request, "Password lama salah")
            return redirect('Porfile')
        if password != ulangi_password:
            messages.error(request, "Password baru dan ulangi password tidak cocok.")
            return redirect('Porfile')
        user.set_password(password)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password berhasil diperbarui.")
        return redirect('Porfile')
def UpdateProfile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        nama = request.POST.get('nama')
        gender = request.POST.get('gender')
        telepon = request.POST.get('telepon')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        if not all([username, nama, gender, telepon, email]):
            messages.error(request, "Semua field harus diisi.")
            return redirect('Porfile')
        user = request.user
        user.username = username
        user.nama = nama
        user.gender = gender
        user.telepon = telepon
        user.email = email
        if image:
            if user.image:
                if os.path.isfile(user.image.path):
                    os.remove(user.image.path)
            user.image = image
        user.save()
        messages.success(request, "Profil berhasil diperbarui.")
        return redirect('Porfile')
    return redirect('Porfile')