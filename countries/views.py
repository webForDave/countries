from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CountrySerializer
from .api_fetcher import get_countries_data
from .models import Country

data = get_countries_data()

@api_view(["POST"])
def refresh_countries(request):
    countries_in_db = Country.objects.all()
    new_data = []

    if countries_in_db:
        Country.objects.all().delete()

    if data == "error fetching":
        return Response({"error": "External data source unavailable", "details": "Could not fetch data from countries API"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    for country in data:
        serializer = CountrySerializer(data=country)

        if serializer.is_valid():
            serializer.save()
            new_data.append(serializer.data)
    return Response(new_data, status=status.HTTP_201_CREATED)

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

@api_view(["GET"])
def get_status(request):    
    countries = Country.objects.all()

    if not countries:
        return Response({"detail": "No data found"}, status=status.HTTP_200_OK)
    else:
        country = Country.objects.first()
        count = countries.count()
        last_refreshed_at = country.last_refreshed_at

        return Response({"total_countries": count, "last_refreshed_at": last_refreshed_at}, status=status.HTTP_200_OK)