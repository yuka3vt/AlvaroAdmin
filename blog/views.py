from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import default_storage
from blog.models import Blog, CategoryBlog
from users.decorators import role_required
from blog.forms import BlogForm
from django.db.models import Count, Q
from django.contrib import messages
from django.urls import reverse
import os
@role_required(['Coach'])
def BlogIndex(request):
    blogs = Blog.objects.filter(user=request.user)
    context = {
            'title' : 'Blog',
            'blogs': blogs
        }
    return render(request, 'blog/BlogIndex.html', context)

@role_required(['Coach'])
def TambahBlog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, f'Blog berhasil ditambahkan.')
            return redirect('BlogIndex')
        else:
            messages.error(request, 'Gagal menambahkan blog. Silakan periksa form dan coba lagi.')
    else:
        form = BlogForm()

    context = {
        'title' : 'Blog',
        'form': form
    }
    return render(request, 'blog/BlogTambah.html', context)
@role_required(['Coach'])
def BlogEdit(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, user=request.user)
    imageL = blog.image.path if blog.image else None
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            if request.FILES.get('image'):
                if imageL and default_storage.exists(imageL):
                    default_storage.delete(imageL)
            blog = form.save()
            if not blog.image and imageL and default_storage.exists(imageL):
                default_storage.delete(imageL)
            form.save()
            messages.success(request, f'Blog berhasil diperbarui.')
            return redirect('BlogIndex')
        else:
            messages.error(request, 'Gagal memperbarui blog. Silakan periksa form dan coba lagi.')
    else:
        form = BlogForm(instance=blog)
    context = {
        'title' : 'Blog',
        'form': form,
        'blog': blog
    }
    return render(request, 'blog/BlogEdit.html', context)
@role_required(['Coach'])
def HapusBlog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if blog.image:
        image_path = blog.image.path
        if default_storage.exists(image_path):
            default_storage.delete(image_path)
    blog.delete()
    messages.success(request, f'Blog berhasil dihapus.')
    return redirect(reverse('BlogIndex')) 

@role_required(['Coach'])
def KategoriIndex(request):
    user = request.user
    kategoris = CategoryBlog.objects.annotate(jumlah_blog=Count('materis'),jumlah_blog_user=Count('materis', filter=Q(materis__user=user)))
    context = {
            'title' : 'Kategori',
            'kategoris': kategoris
        }
    return render(request, 'blog/KategoriIndex.html', context)
@role_required(['Coach'])
def TambahKategori(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        if not nama:
            messages.error(request, "Nama kategori perlu diisi")
            return redirect('KategoriIndex')
        if CategoryBlog.objects.filter(nama=nama).exists():
            messages.error(request, f'Kategori dengan nama "{nama}" sudah ada.')
            return redirect('KategoriIndex')
        
        CategoryBlog.objects.create(nama=nama)
        messages.success(request, f'Kategori berhasil ditambahkan.')
        return redirect('KategoriIndex')
    return redirect('KategoriIndex')
@role_required(['Coach'])
def HapusKategori(request, blog_id):
    kategori = get_object_or_404(CategoryBlog, id=blog_id)
    kategori.delete()
    messages.success(request, f'Kategori "{kategori.nama}" berhasil dihapus.')
    return redirect(reverse('KategoriIndex')) 
@role_required(['Coach'])
def EditKategori(request, blog_id):
    kategori = get_object_or_404(CategoryBlog, id=blog_id)
    if request.method == 'POST':
        nama = request.POST.get('nama')
        if not nama:
            messages.error(request, "Nama kategori perlu diisi")
            return redirect('KategoriIndex')
        if kategori.nama == nama:
            messages.error(request, "Nama kategori tidak berubah")
            return redirect('KategoriIndex')
        if CategoryBlog.objects.filter(nama=nama).exists():
            messages.error(request, f'Kategori dengan nama sudah ada.')
            return redirect('KategoriIndex')
        kategori.nama = nama
        kategori.save()
        messages.success(request, f'Kategori berhasil diubah.')
        return redirect('KategoriIndex')
    return redirect('KategoriIndex')