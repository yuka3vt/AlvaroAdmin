from api.serializers import ProdukSerializer, MembershipSerializer,UserLoginSerializer, BlogSerializer, CategoryBlogSerializer, UserSerializer, MembershipSerializer, TrainerSessionSerializer, TransaksiSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from blog.models import Blog, CategoryBlog
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from trainer.models import TrainerSession
from transaksi.models import Transaksi
from membership.models import Membership
from rest_framework.views import APIView
from datetime import datetime, timedelta
from django.db.models import Count
from rest_framework import status
from django.conf import settings
from produk.models import Produk
from midtransclient import Snap
from django.db.models import Q
from users.models import User
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound

class ExtendTransactionView(APIView):
    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            produk_id = data.get('produk')
            coach_id = data.get('coach')
            jumlah = data.get('jumlah')
            user = User.objects.filter(username=username).first()
            produk = Produk.objects.get(id=produk_id)
            if coach_id:
                coach = User.objects.get(id=coach_id)
                trainer_session = TrainerSession.objects.create(
                    user=user,
                    coach=coach,
                    produk=produk,
                    jumlah_sesi=produk.durasi_hari
                )
                Transaksi.objects.create(
                    invoice=Transaksi.generate_invoice_number(),
                    user=user,
                    nama=f"{produk.nama} ({username})",
                    jenis='Masuk',
                    kategori='Trainer',
                    jumlah=jumlah,
                    status='Berhasil'
                )
                response_data = TrainerSessionSerializer(trainer_session).data
            else:
                tanggal_mulai = datetime.now().date()
                tanggal_akhir = tanggal_mulai + timedelta(days=produk.durasi_hari)
                membership = Membership.objects.create(
                    user=user,
                    produk=produk,
                    tanggal_mulai=tanggal_mulai,
                    tanggal_akhir=tanggal_akhir
                )
                Transaksi.objects.create(
                    invoice=Transaksi.generate_invoice_number(),
                    user=user,
                    nama=f"{produk.nama} ({username})",
                    jenis='Masuk',
                    kategori='Membership',
                    jumlah=jumlah,
                    status='Berhasil'
                )
                response_data = MembershipSerializer(membership).data
            response_data = {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Data fetched successfully",
                "data": response_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        response_data = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Login successful",
            "data": {
                "access": access_token,
                "refresh": str(refresh)
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)
class UserMembershipAPIView(generics.RetrieveAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        user = self.request.user
        if not user:
            raise NotFound("User not found")
        try:
            return Membership.objects.filter(user=user).first()
        except Membership.DoesNotExist:
            raise NotFound("No membership found for this user")
    def get(self, request, *args, **kwargs):
        membership = self.get_object()
        serializer = self.get_serializer(membership)
        return Response({
            "status": "success",
            "status_code": 200,
            "message": "Membership data fetched successfully",
            "data": serializer.data
        })
class UserRiwayatAPIView(generics.ListAPIView):
    serializer_class = TransaksiSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user:
            raise NotFound("User not found")

        username = user.username
        return Transaksi.objects.filter(nama__icontains=username).order_by('-tanggal_transaksi')[:5]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "status_code": 200,
            "message": "Transaksi data fetched successfully",
            "data": serializer.data
        })
class UserTrainerAPIView(generics.RetrieveAPIView):
    serializer_class = TrainerSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        user = self.request.user
        if not user:
            raise NotFound("User not found")
        try:
            return TrainerSession.objects.filter(user=user).first()
        except TrainerSession.DoesNotExist:
            raise NotFound("No Trainer found for this user")
    def get(self, request, *args, **kwargs):
        trainer = self.get_object()
        serializer = self.get_serializer(trainer)
        return Response({
            "status": "success",
            "status_code": 200,
            "message": "Membership data fetched successfully",
            "data": serializer.data
        })
class UserProfileAPIView(APIView):
    def get(self, request):
        try:
            user = request.user
            if user.is_anonymous:
                return Response(
                    {"status": "error", "message": "User not authenticated"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            serializer = UserSerializer(user)
            response_data = {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Data fetched successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self, request):
        try:
            user = request.user
            if user.is_anonymous:
                return Response(
                    {"status": "error", "message": "User not authenticated"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Profile updated successfully",
                    "data": serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            return Response(
                {"status": "error", "message": "Invalid data", "data": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10
class MembershipProdukAPIView(APIView):
    def get(self, request):
        try:
            membership_produk = Produk.objects.filter(tipe='Membership')
            serializer = ProdukSerializer(membership_produk, many=True)
            
            response_data = {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Data fetched successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class TrainerProdukAPIView(APIView):
    def get(self, request):
        try:
            membership_produk = Produk.objects.filter(tipe='Trainer')
            serializer = ProdukSerializer(membership_produk, many=True)
            
            response_data = {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Data fetched successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class BlogAPIView(APIView):
    def get(self, request):
        try:
            kategori_slug = request.query_params.get('kategori')
            search_query = request.query_params.get('search')
            paginator = PageNumberPagination()
            paginator.page_size = 5
            blog_list = Blog.objects.order_by('-updated_at')

            if kategori_slug:
                blog_list = blog_list.filter(category__slug=kategori_slug)

            if search_query: 
                blog_list = blog_list.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

            result_page = paginator.paginate_queryset(blog_list, request)
            serializer = BlogSerializer(result_page, many=True)

            response_data = {
                "status": "success",
                "pagination": {
                    "page": paginator.page.number,
                    "total_pages": paginator.page.paginator.num_pages
                },
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class KategoriBlogView(APIView):
    def get(self, request):
        try:
            blog_list = CategoryBlog.objects.annotate(jumlah_blog=Count('materis'))
            serializer = CategoryBlogSerializer(blog_list, many=True)
            
            response_data = {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Data fetched successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class BlogDetailAPIView(APIView):
    def get(self, request, slug):
        try:
            blog = get_object_or_404(Blog, slug=slug)
            serializer = BlogSerializer(blog)
            response_data = {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Data fetched successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class CoachAPIView(APIView):
    def get(self, request):
        try:
            coach = User.objects.filter(role='Coach')
            serializer = UserSerializer(coach, many=True)
            
            response_data = {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Data fetched successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UserAPIView(APIView):
    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            
            response_data = {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Data fetched successfully",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class PaymentAPIView(APIView):
    def post(self, request):
        try:
            snap = Snap(
                is_production=settings.MIDTRANS['IS_PRODUCTION'],
                server_key=settings.MIDTRANS['SERVER_KEY']
            )
            order_id = request.data.get('order_id')
            gross_amount = request.data.get('gross_amount')
            customer_details = request.data.get('customer_details')
            transaction_data = {
                "transaction_details": {
                    "order_id": order_id,
                    "gross_amount": gross_amount
                },
                "credit_card": {
                    "secure": True
                },
                "customer_details": customer_details
            }
            transaction = snap.create_transaction(transaction_data)
            response_data = {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Transaction created successfully",
                "data": {
                    "token": transaction['token'],
                    "redirect_url": transaction['redirect_url']
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class CreateUserAndTransactionView(APIView):
    def post(self, request):
        try:
            data = request.data
            nama = data.get('nama')
            username = data.get('username')
            email = data.get('email')
            telepon = data.get('telepon')
            produk_id = data.get('produk')
            coach_id = data.get('coach')
            jumlah = data.get('jumlah')
            user = User.objects.create(
                username=username,
                email=email,
                nama=nama,
                telepon=telepon,
                role='User',
            )
            user.set_password('AGM32323')
            user.save()
            produk = Produk.objects.get(id=produk_id)
            if coach_id:
                coach = User.objects.get(id=coach_id)
                trainer_session = TrainerSession.objects.create(
                    user=user,
                    coach=coach,
                    produk=produk,
                    jumlah_sesi=produk.durasi_hari
                )
                Transaksi.objects.create(
                    invoice=Transaksi.generate_invoice_number(),
                    user=user,
                    nama=f"{produk.nama} ({username})",
                    jenis='Masuk',
                    kategori='Trainer',
                    jumlah=jumlah,
                    status='Berhasil'
                )
                response_data = TrainerSessionSerializer(trainer_session).data
            else:
                tanggal_mulai = datetime.now().date()
                tanggal_akhir = tanggal_mulai + timedelta(days=produk.durasi_hari)
                membership = Membership.objects.create(
                    user=user,
                    produk=produk,
                    tanggal_mulai=tanggal_mulai,
                    tanggal_akhir=tanggal_akhir
                )
                Transaksi.objects.create(
                    invoice=Transaksi.generate_invoice_number(),
                    user=user,
                    nama=f"{produk.nama} ({username})",
                    jenis='Masuk',
                    kategori='Membership',
                    jumlah=jumlah,
                    status='Berhasil'
                )
                response_data = MembershipSerializer(membership).data
            response_data = {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Data fetched successfully",
                "data": response_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e),
                "data": None
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

