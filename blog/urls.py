from django.urls import path
from blog.views import BlogIndex,BlogEdit,HapusBlog, TambahBlog,KategoriIndex,TambahKategori, HapusKategori, EditKategori
urlpatterns = [
    path('', BlogIndex, name='BlogIndex'),
    path('tambah/', TambahBlog, name='TambahBlog'),
    path('edit/<int:blog_id>/', BlogEdit, name='BlogEdit'),
    path('hapus/<int:blog_id>/', HapusBlog, name='HapusBlog'),
    path('kategori/', KategoriIndex, name='KategoriIndex'),
    path('kategori/tambah/', TambahKategori, name='TambahKategori'),
    path('kategori/hapus/<int:kategori_id>', HapusKategori, name='HapusKategori'),
    path('kategori/edit/<int:kategori_id>', EditKategori, name='EditKategori'),
]

