from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', include('users.urls')),
    path('transaksi/', include('transaksi.urls')),
    path('trainer/', include('trainer.urls')),
    path('membership/', include('membership.urls')),
    path('blog/', include('blog.urls')),
    path('produk/', include('produk.urls')),
    path('api/', include('api.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)