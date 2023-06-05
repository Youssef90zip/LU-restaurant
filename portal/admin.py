from django.contrib import admin

from portal.models import Kunde, Reservation, Tisch,Gericht,Bestellung,Kategorie, Bestellposition

# Register your models here.
admin.site.register(Kunde)
admin.site.register(Reservation)
admin.site.register(Tisch)
admin.site.register(Gericht)
admin.site.register(Bestellung)
admin.site.register(Kategorie)
admin.site.register(Bestellposition)



