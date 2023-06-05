from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from datetime import datetime, timedelta, time
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import Kunde, Reservation, Tisch
from .models import Gericht, Bestellung, Bestellposition
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def HomePage(request):
    string = ""
    context = {
        'str':string
    }
    return render(request,'HomePage.html',context)
def About(request):

    return render(request,'About.html')

def menu(request):
    gerichte = Gericht.objects.all()
    return render(request, 'Menu.html', {'gerichte': gerichte})

@login_required(login_url='anmeldung')
def menulog(request):
    gerichte = Gericht.objects.all()
    return render(request, 'MenuLog.html', {'gerichte': gerichte})
@login_required(login_url='anmeldung')
def process_order(request):
    if request.method == 'POST':
        gericht_ids = request.POST.getlist('gericht_ids')
        gerichte = Gericht.objects.filter(id__in=gericht_ids)
        gesamtsumme = Decimal(0)
        for gericht in gerichte:
            quantity = int(request.POST.get(f'gericht_{gericht.id}_quantity'))
            preis = gericht.preis
            gesamtsumme += preis * quantity

        bestellung = Bestellung(gesamtsumme=gesamtsumme, kunde=request.user.kunde)
        bestellung.save()

        for gericht in gerichte:
            quantity = int(request.POST.get(f'gericht_{gericht.id}_quantity'))
            if quantity > 0:
                preis = gericht.preis
                bestellposition = Bestellposition(bestellung=bestellung, gericht=gericht, menge=quantity, preis=preis)
                bestellposition.save()
        return redirect('order_confirmation', bestellung_id=bestellung.id)

    else:
        return redirect('menu')

@login_required(login_url='anmeldung')
def order_confirmation(request, bestellung_id):
    try:
        bestellung = Bestellung.objects.get(id=bestellung_id, kunde=request.user.kunde)
        for bestellposition in bestellung.bestellposition_set.all():
            bestellposition.gesamtsumme = bestellposition.menge * bestellposition.preis
        context = {'bestellung': bestellung}
        if request.method == 'POST':
            # Process payment and complete order
            card_number = request.POST.get('card_number')
            expiry_date = request.POST.get('expiry_date')
            cvv = request.POST.get('cvv')
            # Bestellstatus Ändern
            bestellung.is_confirmed = True
            bestellung.save()

            # Email verschicken
            email = request.user.email
            name = request.user.email
            subject = 'Bestellungsbestätigung'
            message = f"Hallo {name},\n" \
                      f"vielen Dank für Ihre Bestellung bei unserem Restaurant.\n" \
                      f"Details zu Ihrer Bestellung:\n" \
                      f"BestellId: {bestellung.id}\n" \
                      f" Gesamtbetrag: {bestellung.gesamtsumme}\n" \
                      f"Beste Grüße,\n" \
                      f"Ihr LU-Restaurant Team"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return redirect('meine_bestellungen', kunde_id=bestellung.kunde.id)
        return render(request, 'OrderConfirmation.html', context)

    except Bestellung.DoesNotExist:
        return redirect('menu')


@login_required(login_url='anmeldung')
def meine_bestellungen(request, kunde_id):
    bestellungen = Bestellung.objects.filter(kunde_id= kunde_id, is_confirmed=True)
    status = 'confirmed'
    return render(request, 'BestellungView.html', {'bestellungen': bestellungen, status: 'status'})


@csrf_protect
def anmeldung(request):
    message = ""
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return  redirect('meine_bestellungen', kunde_id= request.user.kunde.id)
        else:
            message = "Email oder Passwort ist falsch eingegeben"
            return render(request, 'Anmelden.html',{"message":message})
    else:
        return render(request, 'Anmelden.html')

@csrf_protect
def registrierung(request):

    message = ""

    if request.method == 'POST':
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']
        repeatpassword = request.POST['repeatpassword']
        adresse = request.POST['adresse']

        if User.objects.filter(email=email).exists():
            message = "Die eingegebene E-Mail-Adresse ist bereits vergeben."
        elif repeatpassword != password:
            message = "Die eingegebenen Passwörter stimmen nicht überein."
        else:
            # Ein USer Object anlegen
            user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)

            # Ein Kunde object anlegen mit dem user Object verknüpfen
            kunde = Kunde(user=user, lieferadresse=adresse)
            kunde.save()

            # Email verschicken
            subject = 'Bestellungsbestätigung'
            message = f"Hallo {first_name} {last_name},\n" \
                      f"vielen Dank für die Registrierung bei unserem Restaurant.\n" \
                      "Bei Fragenkönnen Sie sich jederzeit an uns wenden. Wir stehen Ihnen gerne zur Verfügung.\n" \
                      f"Beste Grüße,\n" \
                      f"Ihr LU-Restaurant Team"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            # Authentifizierung von dem User
            user = authenticate(request, username=email, password=password)
            login(request, user)

            # Redirect the user to the home page
            return redirect('anmeldung')

    return render(request, 'registrierung.html', {'message': message})

def reservation(request):
        message = ""

        # Handle form submission
        if request.method == 'POST':
            # Get form data
            name = request.POST['name']
            datum = request.POST['date']
            uhrzeit = request.POST['time']
            anzahl = int(request.POST['guests'])
            telnum = request.POST['telnum']
            email = request.POST['email']
            notes = request.POST.get('notes', '')

            # Wir finden die verfügbaren Tische und speichern wir die in reservations
            reservations = Reservation.objects.filter(
                datum=datum,
                uhrzeit=datetime.strptime(request.POST['time'], '%H:%M'),
            )

            reserved_seats = reservations.aggregate(Sum('anzahl'))['anzahl__sum'] or 0
            total_capacity = Tisch.objects.aggregate(Sum('capacity'))['capacity__sum'] or 0
            available_capacity = total_capacity - reserved_seats

            # Falls verfügbare Tische gibt, dann erzeuge eine Reservierung
            if available_capacity >= anzahl:
                available_tables = Tisch.objects.filter(capacity__gte=anzahl)
                if available_tables:
                    reservation = Reservation.objects.create(
                        name=name,
                        tisch=available_tables.first(),
                        datum=datum,
                        uhrzeit=uhrzeit,
                        anzahl=anzahl,
                        telnum=telnum,
                        email=email,
                        notes=notes,
                    )
                    reservation.save()
                    message = "Reservierung erfoltgreich abgeschlossen"
                    # Email verschicken

                    subject = 'Bestellungsbestätigung'
                    body = f"Hallo {name},\n" \
                              f"vielen Dank für Ihre Reservierung bei unserem Restaurant.\n" \
                              f"Details zur Reservierung:\n" \
                              f"Datum: {datum}\n" \
                              f"Uhrzeit: {uhrzeit}\n" \
                              f"Beste Grüße,\n" \
                              f"Ihr LU-Restaurant Team"
                    from_email = settings.DEFAULT_FROM_EMAIL
                    recipient_list = [email]
                    send_mail(subject, body, from_email, recipient_list, fail_silently=False)

                else:
                    message = "No tables available for the specified number of guests"
            else:
                message = "Not enough capacity for the specified number of guests"

        context = {
            'msg': message
        }
        return render(request, 'Reservations.html', context)

def reservationLogin(request):
        message = ""

        # Handle form submission
        if request.method == 'POST':
            # Get form data
            name = request.POST['name']
            datum = request.POST['date']
            uhrzeit = request.POST['time']
            anzahl = int(request.POST['guests'])
            telnum = request.POST['telnum']
            email = request.POST['email']
            notes = request.POST.get('notes', '')

            # Wir finden die verfügbaren Tische und speichern wir die in reservations
            reservations = Reservation.objects.filter(
                datum=datum,
                uhrzeit=datetime.strptime(request.POST['time'], '%H:%M'),
            )

            reserved_seats = reservations.aggregate(Sum('anzahl'))['anzahl__sum'] or 0
            total_capacity = Tisch.objects.aggregate(Sum('capacity'))['capacity__sum'] or 0
            available_capacity = total_capacity - reserved_seats

            # Falls verfügbare Tische gibt, dann erzeuge eine Reservierung
            if available_capacity >= anzahl:
                available_tables = Tisch.objects.filter(capacity__gte=anzahl)
                if available_tables:
                    reservation = Reservation.objects.create(
                        name=name,
                        tisch=available_tables.first(),
                        datum=datum,
                        uhrzeit=uhrzeit,
                        anzahl=anzahl,
                        telnum=telnum,
                        email=email,
                        notes=notes,
                    )
                    reservation.save()
                    message = "Reservierung erfoltgreich abgeschlossen"
                    # Email verschicken

                    subject = 'Bestellungsbestätigung'
                    body = f"Hallo {name},\n" \
                              f"vielen Dank für Ihre Reservierung bei unserem Restaurant.\n" \
                              f"Details zur Reservierung:\n" \
                              f"Datum: {datum}\n" \
                              f"Uhrzeit: {uhrzeit}\n" \
                              f"Beste Grüße,\n" \
                              f"Ihr LU-Restaurant Team"
                    from_email = settings.DEFAULT_FROM_EMAIL
                    recipient_list = [email]
                    send_mail(subject, body, from_email, recipient_list, fail_silently=False)

                else:
                    message = "No tables available for the specified number of guests"
            else:
                message = "Not enough capacity for the specified number of guests"

        context = {
            'msg': message
        }
        return render(request, 'ReservationsLogin.html', context)




