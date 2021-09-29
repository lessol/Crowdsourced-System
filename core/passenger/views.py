import requests
import stripe
import firebase_admin
from firebase_admin import credentials, auth

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from core.passenger import forms

from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.conf import settings

from core.models import *

cred = credentials.Certificate(settings.FIREBASE_ADMIN_CRED)
firebase_admin.initialize_app(cred)

# WILL HAVE TO CHANGE THE PATH OF STRIPE SECRET API KEY
stripe.api_key = settings.STRIPE_SECRET_API_KEY

@login_required
def home(request):
    return redirect(reverse('passenger:profile'))

@login_required(login_url="/sign_in/?next=/passenger/")
def profile_page(request):
    user_form = forms.StandardUserForm(instance=request.user)
    passenger_form = forms.BasicPassengerForm(instance=request.user.passenger)
    password_form = PasswordChangeForm(request.user)

    # change/update user fist name and last name
    if request.method == "POST":

        if request.POST.get('action') == 'update_profile':

            user_form = forms.StandardUserForm(request.POST, instance=request.user)
            passenger_form = forms.BasicPassengerForm(request.POST, request.FILES, instance=request.user.passenger)

            if user_form.is_valid() and passenger_form.is_valid():
                user_form.save()
                passenger_form.save()

                messages.success(request, 'Profile Updated')
                return redirect(reverse('passenger:profile'))

        elif request.POST.get('action') == 'update_password':
    # change/update user password
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)

                messages.success(request, 'Password Updated')
                return redirect(reverse('passenger:profile'))

        elif request.POST.get('action') == 'update_phone':
            # Obtain Freibase User Info/data
            firebase_user = auth.verify_id_token(request.POST.get('id_token'))

            request.user.passenger.phone_number = firebase_user['phone_number']
            request.user.passenger.save()
            return redirect(reverse('passenger:profile'))

    return render(request, 'passenger/profile.html', {
         "user_form": user_form,
         "passenger_form": passenger_form,
         "password_form": password_form,
    })

@login_required(login_url="/sign_in/?next=/passenger/")
def payment_method(request):
    current_customer = request.user.passenger

    # Remove current card ifno
    if request.method == "POST":
        stripe.PaymentMethod.detach(current_customer.stripe_payment_method_id)
        current_customer.stripe_payment_method_id = ""
        current_customer.stripe_card_last4 = ""
        current_customer.save()
        return redirect(reverse('passenger:payment_method'))

    # Save/upload stripe customer info
    if not current_customer.stripe_passenger_id:
        customer = stripe.Customer.create()
        current_customer.stripe_passenger_id = customer['id']
        current_customer.save()

    # Obtain the stripe payment method
    stripe_payment_methods  = stripe.PaymentMethod.list(
        customer = current_customer.stripe_passenger_id,
        type = "card",
    )

    print(stripe_payment_methods)

    if stripe_payment_methods and len(stripe_payment_methods.data) > 0:
        payment_method = stripe_payment_methods.data[0]
        current_customer.stripe_payment_method_id = payment_method.id
        current_customer.stripe_card_last4 = payment_method.card.last4
        current_customer.save()
    else:
        current_customer.stripe_payment_method_id = ""
        current_customer.stripe_card_last4 = ""
        current_customer.save()

    if not current_customer.stripe_payment_method_id:

        intent = stripe.SetupIntent.create(
            customer = current_customer.stripe_passenger_id
        )

        return render(request, 'passenger/payment_method.html', {
            "client_secret": intent.client_secret,
            "STRIPE_PUBLIC_API_KEY": settings.STRIPE_PUBLIC_API_KEY
        })

    else:
        return render(request,'passenger/payment_method.html')


@login_required(login_url="/sign_in/?next=/passenger/")
def create_listing(request):
    current_passenger = request.user.passenger

    if not current_passenger.stripe_payment_method_id: # no payment method setup yet
        return redirect(reverse('passenger:payment_method'))

    has_current_listing = Spot.objects.filter(
        passenger = current_passenger,
        status__in = [
            Spot.PROCESSING_STATUS,
            Spot.DRIVER_EN_ROUTE,
            Spot.DELIVERING,
        ]
    ).exists()

    if has_current_listing:
        messages.warning(request, "A current request for a driver is in progress.")
        return redirect(reverse('passenger:current_listings'))


    creating_listing = Spot.objects.filter(passenger=current_passenger, status=Spot.CREATION_STATUS).last()
    step1_form = forms.SpotCreationStep1Form(instance=creating_listing)
    step2_form = forms.SpotCreationStep2Form(instance=creating_listing)
    step3_form = forms.SpotCreationStep3Form(instance=creating_listing)

    if request.method == "POST":
        if request.POST.get('step') == '1':
            step1_form = forms.SpotCreationStep1Form(request.POST, instance=creating_listing)
            if step1_form.is_valid():
                creating_listing = step1_form.save(commit=False)
                creating_listing.passenger = current_passenger
                creating_listing.save()
                return redirect(reverse('passenger:create_listing'))

        elif request.POST.get('step') == '2':
            step2_form = forms.SpotCreationStep2Form(request.POST, instance=creating_listing)
            if step2_form.is_valid():
                creating_listing = step2_form.save()

                try:
                    r = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins={}&destinations={}&key={}".format(
                        creating_listing.origin_point,
                        creating_listing.end_point,
                        settings.GOOGLE_MAP_API_KEY,
                    ))

                    print(r.json()['rows'])

                    distance = r.json()['rows'][0]['elements'][0]['distance']['value']
                    duration = r.json()['rows'][0]['elements'][0]['duration']['value']
                    creating_listing.distance = round(distance / 1000, 2)
                    creating_listing.duration = int(duration/ 60)
                    creating_listing.price = creating_listing.distance * 1 # $1 per kilometer
                    creating_listing.save()


                except Exception as e:
                    print(e)
                    messages.error(request, "Unfortunately, this destination is not supported")

                return redirect(reverse('passenger:create_listing'))

        elif request.POST.get('step') == '3':
            step3_form = forms.SpotCreationStep3Form(request.POST, request.FILES, instance=creating_listing)
            if step3_form.is_valid():
                creating_listing = step3_form.save(commit=False)
                creating_listing.passenger = current_passenger
                creating_listing.save()
                return redirect(reverse('passenger:create_listing'))

        elif request.POST.get('step') == '4':
            if creating_listing.price:
                try:
                    payment_intent = stripe.PaymentIntent.create(
                        amount = int(creating_listing.price * 100),
                        currency ='usd',
                        customer = current_passenger.stripe_passenger_id,
                        payment_method= current_passenger.stripe_payment_method_id,
                        off_session=True,
                        confirm=True,
                    )

                    Transaction.objects.create(
                        stripe_payment_intent_id = payment_intent['id'],
                        spot = creating_listing,
                        amount = creating_listing.price,
                    )

                    creating_listing.status = Spot.PROCESSING_STATUS
                    creating_listing.save()

                    return redirect(reverse('passenger:home'))

                except stripe.error.CardError as e:
                    err = e.error
                    # Error code will be authentication_required if authentication is needed
                    print("Code is: %s" % err.code)
                    payment_intent_id = err.payment_intent['id']
                    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    
    # Determine the current step
    if not creating_listing:
        current_step = 1
    elif creating_listing.Types_of_Vehicle:
        current_step = 4
    elif creating_listing.end_point:
        current_step = 3
    else:
        current_step = 2

    return render(request, 'passenger/create_listing.html', {
        "spot": creating_listing,
        "step": current_step,
        "step1_form": step1_form,
        "step2_form": step2_form,
        "step3_form": step3_form,
        "GOOGLE_MAP_API_KEY": settings.GOOGLE_MAP_API_KEY
    })

@login_required(login_url="/sign_in/?next=/passenger/")
def current_listings_page(request):
    spot = Spot.objects.filter(
        passenger = request.user.passenger,
        status__in=[
            Spot.PROCESSING_STATUS,
            Spot.DRIVER_EN_ROUTE,
            Spot.PICKED_UP,
            Spot.DELIVERING,
            Spot.DELIVERED,
        ]
    )

    return render(request, 'passenger/spots.html', {
        "spot": spot
    })

@login_required(login_url="/sign_in/?next=/passenger/")
def archived_listings_page(request):
    spot = Spot.objects.filter(
        passenger = request.user.passenger,
        status__in=[
            Spot.COMPLETED_STATUS,
            Spot.CANCELED_STATUS,
        ]
    )

    return render(request, 'passenger/spots.html', {
        "spot": spot
    })

@login_required(login_url="/sign_in/?next=/passenger/")
def listing_page(request, listing_id):
    listing = Spot.objects.get(id=listing_id)

    if request.method == "POST" and listing.status == Spot.AVAILABLE_STATUS:
        listing.status = Spot.CANCELED_STATUS
        listing.save()
        return redirect(reverse('passenger:archived_jobs'))
        
    return render(request, 'passenger/listing.html', {
        "listing":listing,
        "GOOGLE_MAP_API_KEY" : settings.GOOGLE_MAP_API_KEY
    })