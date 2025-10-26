from django.urls import path
from . import views

urlpatterns = [
    path('image', views.serve_summary_image),
    path("", views.get_countries),
    path("refresh", views.refresh_countries),
    path("refresh/", views.refresh_countries),
    path("<str:country_name>", views.get_or_delete_country),
    path("<str:country_name>/", views.get_or_delete_country),
]
