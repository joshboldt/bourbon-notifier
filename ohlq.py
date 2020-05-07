import requests
import re

import pprint

from resources.config import config


def get_stores_in_stock(bourbon_code, all_stores):
    # Returns the store codes of in-stock stores for this bourbon
    request_string = f"https://www.ohlq.com/assets/javascripts/getAgencyInvByProduct.php?code={bourbon_code}"
    req = requests.get(request_string).text
    stores_in_stock = re.findall(r"A\d{4}\w+", req)

    # Generate store info for each in-stock store
    stocked_stores_with_info = []
    for store in stores_in_stock:
        store_info = all_stores.get(store[1:])  # Removes 'A' Agency character
        if store_info != None:
            stocked_stores_with_info.append(store_info)

    return stocked_stores_with_info


def get_all_stores():
    # Gets all valid stores from OHLQ
    def parse_stores(raw_stores_text):
        # Parses the stores into a dictionary accessible by store code
        store_list = list(raw_stores_text[15:].split("],["))
        stores_dict = {}
        for store in store_list:
            store_info = str(store).split(",")
            store_address = "{}, {}, {}".format(
                re.sub('[",]', "", store_info[2]),
                re.sub('[",]', "", store_info[3]),
                re.sub('[",]', "", store_info[4]),
            )
            store_dict = dict(
                store_code=store_info[0].replace("[[", "").replace('"', ""),
                name=store_info[1].replace('"', ""),
                address=store_address,
                zip_code=store_info[5].replace('"', ""),
                phone_number=store_info[6].replace('"', ""),
            )
            stores_dict[store_info[0].replace("[[", "").replace('"', "")] = store_dict

        return stores_dict

    request_string = "https://www.ohlq.com/assets/javascripts/jsonDistro.php?d=av2"
    req = requests.get(request_string)
    parsed_store_dict = parse_stores(req.text)

    return parsed_store_dict


def get_stores_by_location(in_stock_stores, location_list):
    # Filter though each zip code and finding the matching stores
    localized_stores = {}
    for location in location_list:
        print(f"Checking for in-stock stores in {location}")
        # Filter through each stores and see if it is in the target zip code
        for target_store in in_stock_stores:
            if location == target_store.get("zip_code"):
                store_code = target_store.get("store_code")
                store_name = target_store.get("name")
                localized_stores.update({store_code: store_name})

    return localized_stores


def main():

    # 0. App config
    bourbon_list = config.get("bourbons")
    locations = config.get("locations")

    # 1. Generate updated store list
    store_list = get_all_stores()

    result = []

    for name, key in bourbon_list.items():
        # 2. Get all stores for the given bourbon into a dictionary
        print(f"\n\nChecking stores for {name}...")
        in_stock_stores = get_stores_in_stock(key, store_list)
        if not in_stock_stores:
            print(f"No stores have {name} in-stock at this time...")
        else:
            # 3. Filter stores down by location
            localized_stores = get_stores_by_location(in_stock_stores, locations)
            pprint.pprint(localized_stores)

            return localized_stores