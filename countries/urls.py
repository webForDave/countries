from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_country),
    path("refresh", views.refresh_countries),
    path("refresh/", views.refresh_countries),
    path("<str:country_name>", views.get_or_delete_country),
    path("<str:country_name>/", views.get_or_delete_country),

]
