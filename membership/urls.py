from django.urls import path
from membership.views import MemberDetails, MembershipBaru, TambahMembership
urlpatterns = [
    path('index/', MemberDetails, name='MemberDetails'),
    path('baru/', MembershipBaru, name='MembershipBaru'),
    path('tambah/', TambahMembership, name='TambahMembership'),
]