from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# BURASI DEĞİŞİYOR:
from pages.views import index   # <-- kendi boş fonksiyonunu kaldır, bunu ekle

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),  # <-- artık pages/views.py içindeki fonksiyonu çağırıyor
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
