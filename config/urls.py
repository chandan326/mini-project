from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('crops/', include('crops.urls')),
    path('diseases/', include('diseases.urls')),
    path('diagnosis/', include('diagnosis.urls')),
    path('reports/', include('reports.urls')),
    
    # API endpoints
    path('api/crops/', include('crops.api_urls')),
    path('api/diseases/', include('diseases.api_urls')),
    path('api/diagnosis/', include('diagnosis.api_urls')),
    path('api/reports/', include('reports.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
