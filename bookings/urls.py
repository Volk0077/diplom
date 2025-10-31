from django.urls import path
from . import views


app_name = "bookings"

urlpatterns = [
    path("my/", views.my_bookings, name="my_bookings"),
    path("create/", views.create_booking, name="create_booking"),
    path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
    path("api/staff/", views.api_staff_list, name="api_staff_list"),
    path("api/services/", views.api_services_list, name="api_services_list"),
]
