from datetime import datetime
import requests
import json
import os

ALL_TGC = {}

api_key = '11K87Y4BHRXHD605JVO5KFF5WJWO0QJ7TQOYVP3J5N48U2E6OQL94MY44OUA0235MI9CJ3YV7GFFIONA'


def get_pokemons():
    # Your ScrapingBee API key

    # The target URL you want to scrape
    url = 'https://www.pokemon.com/api/1/us/expansions/get-expansions.json?index=0&count=10000'

    # Parameters for ScrapingBee API
    params = {
        'api_key': api_key,
        'url': url,
        'forward_headers': 'true',  # Optional: forward headers to the target website
        'render_js': 'false',  # Set to 'true' if JavaScript needs to be executed
        'wait': 1000  # Optional: wait for 1000 milliseconds if the page has delayed content
    }

    # Sending the request to ScrapingBee
    response = requests.get('https://app.scrapingbee.com/api/v1/', params=params, timeout=60)

    # print(response.status_code)

    # Parse the JSON response
    data = response.json()

    # # Save the data to a JSON file
    # with open("pokemon.json", "w", encoding="utf-8") as f:
    #     json.dump(data, f, indent=4)

    # with open("pokemon.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)

    # Current date
    current_date = datetime.now()

    # Function to convert string date to datetime object
    def parse_date(date_str):
        return datetime.strptime(date_str, '%B %d, %Y')

    # Filtered data containing only past releases
    past_releases = [entry for entry in data if parse_date(entry['releaseDate']) < current_date]

    data_date_filtered = {}
    # Print the filtered data
    for release in past_releases:
        data_date_filtered[release['title']] = release

    with open("pokemon_date_filtered.json", "w", encoding="utf-8") as f:
        json.dump(data_date_filtered, f, indent=4)


def get_tgc_list():
    data = None
    with open("pokemon_date_filtered.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    if data == None:
        print("error in reading data in get_tgc_list function")

    for title in data:
        pokemon = data[title]
        get_tgc_data(title)
    with open(f"all_tgc_data.json", "w", encoding="utf-8") as f:
        json.dump(ALL_TGC, f, indent=4)


def make_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully.")


def get_tgc_data(title, page=0):
    try:
        print("getting tgc data of:", title, " page:", page)

        start = page * 50

        end = 50

        url = f'https://mp-search-api.tcgplayer.com/v1/search/request?q={title}'
        body = '{"algorithm":"sales_synonym_v2","from":' + str(start) + ',"size":' + str(
            end) + ',"filters":{"term":{"productLineName":["pokemon"]},"range":{},"match":{}},"listingSearch":{"context":{"cart":{}},"filters":{"term":{"sellerStatus":"Live","channelId":0},"range":{"quantity":{"gte":1}},"exclude":{"channelExclusion":0}}},"context":{"cart":{},"shippingCountry":"CA","userProfile":{}},"settings":{"useFuzzySearch":true,"didYouMean":{}},"sort":{}}'

        # print(body)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Content-Type': "application/json",
            'Cookie': 'TCG_VisitorKey=9388c520-b78a-41b6-8b50-14fde879839e',
            'Origin': 'null'
        }

        # response = requests.get(url , data=body , headers=headers)

        # Parameters for ScrapingBee API
        params = {
            'api_key': api_key,
            'url': url,
            'forward_headers': 'true',  # Optional: forward headers to the target website
            'render_js': 'false',  # Set to 'true' if JavaScript needs to be executed
            'wait': 1000  # Optional: wait for 1000 milliseconds if the page has delayed content
        }

        # Sending the request to ScrapingBee
        response = requests.post('https://app.scrapingbee.com/api/v1/', params=params, headers=headers, data=body,
                                 timeout=60)

        # print(response.status_code)

        if response.status_code == 200:
            my_data = response.json()["results"][0]["results"]
            total_size = int(response.json()["results"][0]["totalResults"])
            # print(my_data)
            make_folder(title)
            with open(f"{title}/tgc_data_{title}_{page}.json", "w", encoding="utf-8") as f:
                json.dump(my_data, f, indent=4)
            if not title in ALL_TGC:
                ALL_TGC[title] = []
            ALL_TGC[title].append(my_data)
            if start + end <= total_size:
                get_tgc_data(title, page + 1)
    except Exception as e:
        print("error in getting tgc data of:", title, " page:", page, e)


def start():
    get_pokemons()
    get_tgc_list()

start()