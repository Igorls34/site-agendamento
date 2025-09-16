"""
URL configuration for agendamento project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from bookings.views import favicon_view

urlpatterns = [
    path('secret-dev-access-f7b8c9d2e1a3/', admin.site.urls),  # URL secreta para desenvolvedor apenas
    path('profissional/', include('bookings.admin_urls')),  # Nova interface para profissional
    path('favicon.ico', favicon_view, name='favicon'),
    path('', include('bookings.urls')),
]
