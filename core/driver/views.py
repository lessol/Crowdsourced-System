from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings

from core.models import *

@login_required(login_url="/sign-in/?next=/driver/")
def home(request):
    return redirect(reverse('driver:available_spots'))

@login_required(login_url="/sign-in/?next=/driver/")
def available_spots_page(request):
    return render(request, 'driver/available_spots.html', {
    "GOOGLE_MAP_API_KEY": settings.GOOGLE_MAP_API_KEY})

@login_required(login_url="/sign-in/?next=/driver/")
def spot_details_page(request, id):
    listing = Spot.objects.filter(id=id, status=Spot.PROCESSING_STATUS).last()

    if not listing:
        return redirect(reverse('driver:available_spots'))

    if request.method == 'POST':
        listing.driver = request.user.driver
        listing.status = Spot.DRIVER_EN_ROUTE
        listing.save()

        return redirect(reverse('driver:available_spots'))

    return render(request, 'driver/spot_details.html', {
        "listing":listing
    })

@login_required(login_url="/sign-in/?next=/driver/")
def current_listing_page(request):
    listing = Spot.objects.filter(
        driver=request.user.driver,
        status__in = [
            Spot.DRIVER_EN_ROUTE,
            Spot.PICKED_UP,
            Spot.DELIVERING,
        ]
    ).last()

    return render(request, 'driver/current_listing.html', {
        "listing": listing,
        "GOOGLE_MAP_API_KEY": settings.GOOGLE_MAP_API_KEY
    })

@login_required(login_url="/sign-in/?next=/driver/")
def current_listing_arrival_photo_page(request, id):
    listing = Spot.objects.filter(
        id=id,
        driver = request.user.driver,
        status__in = [
            Spot.DRIVER_EN_ROUTE,
            Spot.DELIVERING
        ]
    ).last()

    if not listing:
        return redirect(reverse('driver:current_listing'))

    return render(request, 'driver/current_listing_arrival_photo.html', {
        "listing": listing
    })

@login_required(login_url="/sign-in/?next=/driver/")
def spot_complete_page(request):
    return render(request, 'driver/spot_complete.html')

@login_required(login_url="/sign-in/?next=/driver/")
def archived_spots_page(request):
    spots = Spot.objects.filter(
        driver = request.user.driver,
        status = Spot.COMPLETED_STATUS
    )
    return render(request, 'driver/archived_spots.html', {
        "spots": spots
    })

@login_required(login_url="/sign-in/?next=/driver/")
def profile_page(request):
    spots = Spot.objects.filter(
        driver = request.user.driver,
        status = Spot.COMPLETED_STATUS
    )

    total_earned = round(sum(spot.price for spot in spots) * 0.85, 2)
    total_drives = len(spots)
    total_km = sum(spot.distance for spot in spots)

    return render(request, 'driver/profile.html', {
        "total_earned": total_earned,
        "total_drives": total_drives,
        "total_km" : total_km
    })