from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from datetime import timedelta, datetime, date
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

# Create your models here.

    # user = models.ForeignKey(User, on_delete=models.CASCADE, null= True,default=None)
    # da Hätte man das besser lösen könne, bei der Nutzung von OnetoOneField()
class Kunde(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=None)
    lieferadresse = models.CharField(max_length=512)

    def __str__(self):
        if self.user:
            return self.user.email
        else:
            return f"Kunde {self.id} (No User)"

class Tisch(models.Model):

    nummer = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField(default= 5)
    def __str__(self):
        return str(self.nummer)
class Reservation(models.Model):

    name = models.CharField(max_length=15)
    tisch = models.ForeignKey(Tisch, on_delete=models.CASCADE, related_name="reservations", default =1)
    datum = models.DateField()
    uhrzeit = models.TimeField()
    anzahl = models.PositiveIntegerField()
    email = models.CharField(max_length=256, default ="")
    telnum = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" {self.name}- {self.datum} - {self.uhrzeit}"
class Kategorie(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=100)
class Gericht(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100)
    beschreibung = models.TextField()
    preis = models.DecimalField(max_digits=8, decimal_places=2)
    kategorie = models.ForeignKey(Kategorie, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gerichte/', blank=True, null=True)


class Bestellung(models.Model):

    def __str__(self):
        return f"Bestellung {self.id}"

    kunde = models.ForeignKey(Kunde, on_delete=models.CASCADE, null= True, blank= True)
    gerichte = models.ManyToManyField(Gericht)
    datum = models.DateField(auto_now_add=True,null= True, blank= True)
    gesamtsumme = models.DecimalField(max_digits=8, decimal_places=2,null= True, blank= True)
    is_confirmed = models.BooleanField(default=False)  # New field added to represent whether the order is confirmed or not

class Bestellposition(models.Model):

    def __str__(self):
        return f"{self.gericht} x {self.menge} ({self.bestellung.kunde.email})"

    bestellung = models.ForeignKey(Bestellung, on_delete=models.CASCADE)
    gericht = models.ForeignKey(Gericht, on_delete=models.CASCADE)
    menge = models.IntegerField()
    preis = models.DecimalField(max_digits=8, decimal_places=2)












def validate (email, password):

    angemeldet = False
    sql = Kunde.objects.raw("SELECT id FROM portal_kunde WHERE email = %s AND password = %s", [email, password])

    if len(sql) > 0:
       angemeldet = True

    return angemeldet

# das ist eine Lücke für SQL-Injections !!!
def userexists(email):
    exists = False
    sql = Kunde.objects.raw("SELECT id FROM portal_kunde WHERE email = %s", [email])

    if len(sql) > 0:
        exists = True
    return exists

def valide(email, password):
    user = authenticate(username=email, password=password)
    return user is not None

def hash(password):

    hashed_password = make_password(password, salt= None, hasher="default")
    return hashed_password

