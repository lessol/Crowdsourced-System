from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from core.models import *

@csrf_exempt
@login_required(login_url="/user/sign-in/")
def available_spots_api(request):
    spots = list(Spot.objects.filter(status=Spot.PROCESSING_STATUS).values())

    return JsonResponse({
        "success": True,
        "spots": spots
    })

@csrf_exempt
@login_required(login_url="/user/sign-in/")
def current_spot_update_api(request, id):
    listing= Spot.objects.filter(
        id=id,
        driver=request.user.driver,
        status__in=[
            Spot.DRIVER_EN_ROUTE,
            Spot.PICKED_UP,
            Spot.DELIVERING
        ]
    ).last()

    if listing.status == Spot.DRIVER_EN_ROUTE:
        listing.origin_photo = request.FILES['origin_photo']
        listing.origin_at = timezone.now()
        listing.status = Spot.DELIVERING
        listing.save()

    elif listing.status == Spot.DELIVERING:
        listing.end_photo = request.FILES['end_photo']
        listing.end_at = timezone.now()
        listing.status = Spot.COMPLETED_STATUS
        listing.save()

    return JsonResponse({
        "success":True
    })
