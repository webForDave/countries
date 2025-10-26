from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CountrySerializer
from .api_fetcher import get_countries_data
from django.db import transaction
from .models import Country
from django.http import FileResponse 
from .image_generator import generate_summary_image, IMAGE_PATH
import os, mimetypes

data = get_countries_data()

@api_view(["POST"])
def refresh_countries(request):

    data = get_countries_data()

    if data == "error fetching":
        return Response(
            {"error": "External data source unavailable", "details": "Could not fetch data from external APIs"}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        with transaction.atomic():
            # 1. Delete ALL existing records
            Country.objects.all().delete()
            
            # 2. Insert new records and collect data for image generation
            top_countries_data = []
            for country_data in data:
                serializer = CountrySerializer(data=country_data)

                if serializer.is_valid():
                    country_instance = serializer.save()
                    # Collect required fields for image generation
                    top_countries_data.append({
                        'name': country_instance.name,
                        'estimated_gdp': country_instance.estimated_gdp
                    })
                else:
                    # Log validation error if needed, but continue for other countries
                    print(f"Validation failed for a country: {serializer.errors}")

            total_countries = Country.objects.count()
            last_refreshed_at = Country.objects.first().last_refreshed_at if total_countries > 0 else None
            
            top_countries = Country.objects.all().order_by('-estimated_gdp')[:5].values('name', 'estimated_gdp')

            if total_countries > 0:
                generate_summary_image(total_countries, last_refreshed_at, list(top_countries))

        return Response({"message": f"Successfully refreshed {total_countries} countries."}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": "Internal server error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["GET"])
def get_status(request):
    countries = Country.objects.all()
    count = countries.count()
    last_refreshed_at = None

    if count > 0:
        last_refreshed_at = countries.first().last_refreshed_at

    return Response({
        "total_countries": count, 
        "last_refreshed_at": last_refreshed_at
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_summary_image(request):
    """
    GET /countries/image -> Serves the generated summary image or an error.
    """
    if os.path.exists(IMAGE_PATH):
        try:
            mime_type, encoding = mimetypes.guess_type(IMAGE_PATH)
            if mime_type is None:
                mime_type = 'application/octet-stream'
                
            return FileResponse(open(IMAGE_PATH, 'rb'), content_type=mime_type)
        except Exception as e:
            return Response(
                {"error": "Internal server error", "details": "Could not serve image file."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return Response(
            {"error": "Summary image not found"},
            status=status.HTTP_200_OK
        )


@api_view(["GET"])
def get_countries(request):

    region = request.query_params.get("region")
    currency = request.query_params.get("currency")

    if region:
        countries = Country.objects.filter(region=region)
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif currency:
        countries = Country.objects.filter(currency_code=currency)
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET", "DELETE", "PUT"])
def get_or_delete_country(request, country_name):

    if request.method == "GET":
        try:
            country = Country.objects.get(name__iexact=country_name)
            serializer = CountrySerializer(country)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Country.DoesNotExist:
            return Response({"detail": "Country does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == "DELETE":
        try:
            country = Country.objects.get(name__iexact=country_name)
            country.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Country.DoesNotExist:
            return Response({"detail": "Country does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == "PUT":
        try:
            country = Country.objects.get(name__iexact=country_name)
        except Country.DoesNotExist:
            return Response({"error": "Country not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CountrySerializer(instance=country, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)