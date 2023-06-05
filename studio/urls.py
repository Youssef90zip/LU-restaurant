"""studio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from portal.views import HomePage
from portal.views import anmeldung
from portal.views import registrierung
from portal.views import reservation, HomePage, process_order, order_confirmation, meine_bestellungen, menu, menulog, reservationLogin

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePage, name= 'HomePage'),
    path('Menu/', menu, name='menu'),
    path('MenuLog/', menulog, name='menulog'),
    path('Reservations/', reservation, name='reservierung'),
    path('ReservationsLogIn/', reservationLogin, name='reservierungLogin'),
    path('ProcessOrder/', process_order, name='process_order'),
    path('HomePage/', HomePage, name='homepage'),
    path('Anmelden/', anmeldung, name='anmeldung'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/Anmelden/'), name='logout'),
    path('Registrierung/', registrierung, name='registrierung'),
    path('order_confirmation/<int:bestellung_id>/', order_confirmation, name='order_confirmation'),
    path('MeineBestellung/<int:kunde_id>/', meine_bestellungen, name='meine_bestellungen')

     ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

