from django.contrib import admin
from django.contrib import auth
from django.urls import path, include
from django.contrib.auth import views as a_views
from django.conf import settings
from django.conf.urls.static import static

from core import views

from core.passenger import views as passenger_views
from core.driver import views as driver_views, apis as driver_apis

passenger_urlpatterns = [
    path('', passenger_views.home, name="home"),
    path('profile/', passenger_views.profile_page, name="profile"),
    path('payment_method/', passenger_views.payment_method, name="payment_method"),
    path('create_listing/', passenger_views.create_listing, name="create_listing"),
    path('listings/current', passenger_views.current_listings_page, name="current_listings"),
    path('listings/archived', passenger_views.archived_listings_page, name="archived_listings"),

    path('listings/<listing_id>/', passenger_views.listing_page, name="listing"),

]

driver_urlpatterns = [
    path('', driver_views.home, name="home"),
    path('spots/available/', driver_views.available_spots_page, name="available_spots"),
    path('spots/available/<id>/', driver_views.spot_details_page, name="spot_details"),
    path('spots/current/', driver_views.current_listing_page, name="current_listing"),
    path('spots/current/<id>/arrival_photo/', driver_views.current_listing_arrival_photo_page, name="current_listing_arrival_photo"),
    path('spots/complete', driver_views.spot_complete_page, name="spot_complete"),
    path('spots/archived/', driver_views.archived_spots_page, name="archived_spots"),
    path('profile/', driver_views.profile_page, name="profile"),

    path('api/spots/available/', driver_apis.available_spots_api, name="available_spots_api"),
    path('api/spots/current/<id>/update/', driver_apis.current_spot_update_api, name="current_spot_update_api"),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),
    path('', views.home),
    
    path('sign-in/', a_views.LoginView.as_view(template_name="sign_in.html")),
    path('sign-out/', a_views.LogoutView.as_view(next_page="/")),
    path('sign-up/', views.sign_up),

    path('passenger/', include((passenger_urlpatterns,'passenger'))),
    path('driver/', include((driver_urlpatterns,'driver'))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)