import httpx, random, datetime

countries_data_url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
exchannge_rates_data_url = "https://open.er-api.com/v6/latest/USD"

def fetch_exchange_rates_data() -> dict:
    try: 
        data = httpx.get(exchannge_rates_data_url).json()
        return data
    except Exception as e:
        return {"Error fetching data from exchange rates API": e}
    
rates = fetch_exchange_rates_data()["rates"]

def fetch_countries_data() -> list:
    countries = []

    try:
        data = httpx.get(countries_data_url).json()
    except Exception as e:
        return {"Error fetching countries data": e}
    
    for country in data:

        if not country.get("capital"): capital = None
        else: capital = country["capital"]

        if not country.get("currencies") or len(country["currencies"]) == 0:
            currency_code = None
            exchange_rate = None
            estimated_gdp = 0
        else:
            for currency in country["currencies"][0:1]:
                currency_code = currency["code"]

                for rate_key, rate_value in rates.items():
                    if currency_code == rate_key:
                        exchange_rate = rate_value
                        estimated_gdp = round((country["population"] * random.randint(1000, 2000)) / exchange_rate, 1)

        countries.append({
            "name": country["name"],
            "capital": capital,
            "region": country["region"],
            "population": country["population"],
            "currency_code": currency_code,
            "exchange-rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": country["flag"],
            "last_refreshed_at": datetime.datetime.utcnow().isoformat() + "Z"

        })

    return countries 

print(fetch_countries_data())