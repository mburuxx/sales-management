"""
URL configuration for salesmgt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('store.urls')),
]

if settings.DEBUG:
    # It is good practice to add static files too, even if you are only 
    # seeing issues with the media handler.
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # This is the line that was causing the conflict:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)