from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from admin_dashboard.views import custom_admin_dashboard
from django.views.generic import RedirectView

urlpatterns = [
    # Custom admin dashboard (override admin index)
    path('admin/', custom_admin_dashboard, name='admin_index_custom'),

    # If user visits '/admin/fitur/' exactly, redirect back to custom dashboard '/admin/'
    path('admin/fitur/', RedirectView.as_view(url='/admin/', permanent=False), name='admin_fitur_index_redirect'),

    # Keep built-in admin features under /admin/fitur/ for all other admin pages
    path('admin/fitur/', admin.site.urls),

    # Tambahkan rute untuk aplikasi Anda di sini
    path('', include('admin_dashboard.urls')),
]

# Tambahkan konfigurasi untuk file statis saat development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)