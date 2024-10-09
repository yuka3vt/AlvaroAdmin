from api.views import ExtendTransactionView,UserLoginView,UserRiwayatAPIView,UserTrainerAPIView,UserProfileAPIView,UserMembershipAPIView, MembershipProdukAPIView, BlogAPIView, KategoriBlogView, TrainerProdukAPIView, BlogDetailAPIView, CoachAPIView, UserAPIView, PaymentAPIView, CreateUserAndTransactionView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('membership-produk/', MembershipProdukAPIView.as_view(), name='MembershipProdukAPIView'),
    path('trainer-produk/', TrainerProdukAPIView.as_view(), name='TrainerProdukAPIView'),
    path('blog/', BlogAPIView.as_view(), name='BlogAPIView'),
    path('coach/', CoachAPIView.as_view(), name='CoachAPIView'),
    path('users/', UserAPIView.as_view(), name='UserAPIView'),
    path('blog-kategori/', KategoriBlogView.as_view(), name='KategoriBlogView'),
    path('blog/<slug:slug>/', BlogDetailAPIView.as_view(), name='BlogDetailAPIView'),
    path('payment/', PaymentAPIView.as_view(), name='PaymentAPIView'),
    path('buat-transaksi/', CreateUserAndTransactionView.as_view(), name='CreateUserAndTransactionView'),
    path('login/', UserLoginView.as_view(), name='UserLoginView'),
    path('profile/', UserProfileAPIView.as_view(), name='UserProfileAPIView'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-membership/', UserMembershipAPIView.as_view(), name='UserMembershipAPIView'),
    path('user-trainer/', UserTrainerAPIView.as_view(), name='UserTrainerAPIView'),
    path('user-riwayat/', UserRiwayatAPIView.as_view(), name='UserRiwayatAPIView'),
    path('perpanjang-transaksi/', ExtendTransactionView.as_view(), name='ExtendTransactionView'),
]
