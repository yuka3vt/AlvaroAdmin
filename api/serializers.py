from rest_framework import serializers
from produk.models import Produk
from blog.models import Blog,CategoryBlog
from users.models import User
from transaksi.models import Transaksi
from membership.models import Membership
from trainer.models import TrainerSession, TrainingSchedule
from django.contrib.auth import authenticate


class TrainingScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSchedule
        fields = ['id', 'nama', 'mulai', 'selesai', 'deskripsi']

class ProdukSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produk
        fields = ['id', 'nama', 'deskripsi', 'tipe', 'durasi_hari', 'harga']

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nama', 'telepon', 'image', 'role', 'gender', 'date_joined']

class CategoryBlogSerializer(serializers.ModelSerializer):
    jumlah_blog = serializers.IntegerField(read_only=True)
    class Meta:
        model = CategoryBlog
        fields = ['id', 'nama', 'slug', 'jumlah_blog']

class BlogSerializer(serializers.ModelSerializer):
    user = UserSerializer() 
    category = CategoryBlogSerializer()
    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'description', 'content', 'image', 'created_at', 'updated_at', 'user', 'category']

class TransaksiSerializerView(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Transaksi
        fields = ['id', 'invoice', 'user', 'nama', 'jenis', 'kategori', 'keterangan', 'jumlah', 'status', 'tanggal_transaksi']

class TransaksiSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Transaksi
        fields = ['id', 'invoice', 'user', 'nama', 'jenis', 'kategori', 'keterangan', 'jumlah', 'status', 'tanggal_transaksi']
    def create(self, validated_data):
        validated_data['invoice'] = Transaksi.generate_invoice_number()
        return super().create(validated_data)
    
class MembershipSerializer(serializers.ModelSerializer):
    produk = ProdukSerializer()
    class Meta:
        model = Membership
        fields = ['user', 'produk', 'tanggal_mulai', 'tanggal_akhir']

class TrainerSessionSerializer(serializers.ModelSerializer):
    produk = ProdukSerializer()
    coach = UserSerializer()
    schedules = TrainingScheduleSerializer(many=True, read_only=True)
    class Meta:
        model = TrainerSession
        fields = ['id', 'user', 'coach', 'produk', 'jumlah_sesi', 'status', 'schedules']

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        if user.role != 'User':
            raise serializers.ValidationError('Access denied for non-user roles')
        attrs['user'] = user
        return attrs
