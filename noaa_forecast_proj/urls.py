"""noaa_forecast_proj URL Configuration

"""
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from forecasts import views
from forecasts.views import DashboardView
from forecasts.views import HomeView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),    
    path('forecasts/', include('forecasts.urls')),
    path('accounts/', include('accounts.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)