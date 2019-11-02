import pycountry

COUNTRY_TO_CODE = {
    "Virgin Islands (USA)": "VIR",
    "Iran (Islamic Rep of)": "IRN",
    "Venezuela (Bolivarian Republic of)": "VEN",
    "Saint Vincent and Grenadines": "VCT",
    "TFYR Macedonia": "MKD",
    "Occupied Palestinian Territory": "PSE",
    "Macau": "MAC",
    "Reunion": "REU"
    }  # get codes for some countries that are not easily found in pycountry


def get_alpha3_code(country_name: str) -> str:
    """
    Get the alpha_3 code for a country (e.g. FRA for France), using pycountry library
    :param country_name: string, name of country we want code for
    :return: string, the alpha_3 code. If cannot find code then return empty string
    """
    try:
        return pycountry.countries.get(name=country_name).alpha_3
    except AttributeError:
        try:
            alpha3_fuzzy = pycountry.countries.search_fuzzy(country_name)
        except LookupError:
            try:
                return pycountry.historic_countries.get(name=country_name).alpha_3
            except AttributeError:
                alpha3_use_dict = COUNTRY_TO_CODE.get(country_name, "")
                if alpha3_use_dict == "":
                    print(f"Could not find alpha-3 code for country {country_name}")
                return alpha3_use_dict

        # if len(alpha3_fuzzy) > 1:
        #     print(f"Multiple possibilities found for country {country_name} (taking first one): {alpha3_fuzzy}")
        return alpha3_fuzzy[0].alpha_3
