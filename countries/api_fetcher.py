import requests, random, datetime

COUNTRIES_DATA_URL = 'https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies'
EXCHANGE_DATA_URL = 'https://open.er-api.com/v6/latest/USD'

def get_exchange_rates() -> dict:
    try:
        data = requests.get(EXCHANGE_DATA_URL).json()
        return data["rates"]
    except Exception as e:
        return e
    
exchange_rates = get_exchange_rates()
    
def get_countries_data() -> list:
    countries = []
    try:
        data = requests.get(COUNTRIES_DATA_URL).json()
    except Exception as e:
        return e
    
    for country in data:

        if not country.get("capital"):
            capital = None
        else:
            capital = country["capital"]

        if not country.get("currencies"):
            currency_code = None
            exchange_rate = None
            estimated_gdp = None
        else:
            if len(country["currencies"]) > 1:
                for currency in country["currencies"][0:1]:
                    currency_code = currency["code"]
            currency_code = country["currencies"][0]["code"]

            for rate_code, rate_value in exchange_rates.items():
                if rate_code == currency_code:
                    exchange_rate = round(rate_value, 2)
                    estimated_gdp = round((country["population"] * random.randint(1000, 2000)) / exchange_rate, 1)

        countries.append({
            "name": country["name"],
            "capital": capital,
            "region": country["region"],
            "population": country["population"],
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": country["flag"],
            "last_refreshed_at": datetime.datetime.utcnow().isoformat() + "Z"
        })

    return countries