from django.urls import path
from . import views


app_name = "bookings"

urlpatterns = [
    path("my/", views.my_bookings, name="my_bookings"),
    path("create/", views.create_booking, name="create_booking"),
]
