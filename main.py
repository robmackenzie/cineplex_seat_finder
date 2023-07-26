import requests
from bs4 import BeautifulSoup as bs
import datetime
import json

def longest_false_streak(lst):
    max_streak = 0
    current_streak = 0

    for item in lst:
        if item is False:
            current_streak += 1
        else:
            max_streak = max(max_streak, current_streak)
            current_streak = 0

    # In case the longest streak is at the end of the list
    max_streak = max(max_streak, current_streak)
    return max_streak


def get_json_from_script_tag(url):
    # Fetch the HTML content from the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch URL: {url}")
        return None

    # Parse the HTML content using BeautifulSoup
    soup = bs(response.content, 'html.parser')

    # Find all script tags in the HTML
    script_tags = soup.find_all('script')

    # Search for the script tag containing the target variable (seatMapViewModelInfo)
    for script_tag in script_tags:
        script_content = script_tag.string
        if script_content and 'seatMapViewModelInfo' in script_content:
            # Extract the JSON object from the script content
            start_index = script_content.find('{')
            end_index = script_content.rfind('}') + 1
            json_data = script_content[start_index:end_index]

            # Parse the JSON object and return it
            try:
                return json.loads(json_data)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
                return None

    print("Variable 'seatMapViewModelInfo' not found in any script tags.")
    return None

if __name__ == '__main__':
        all_shows=[]
        r = requests.get("https://apis.cineplex.com/prod/cpx/theatrical/api/v1/showtimes?language=en&locationId=1405&filmId=35397",
            #r = requests.get("https://apis.cineplex.com/prod/cpx/theatrical/api/v1/showtimes?language=en&locationId=1405&date="+(datetime.date.today()+datetime.timedelta(days=1)).strftime("%m/%d/%Y")+"&experiences=imax",
                         headers={"Ocp-Apim-Subscription-Key": "dcdac5601d864addbc2675a2e96cb1f8"})
        r.raise_for_status()
        for date in r.json()[0]['dates']:#
            for show in date['movies'][0]['experiences'][0]['sessions']:
                 all_shows.append(show)
        seat_maps={}
        for show in all_shows:
             rows_i_care_about = get_json_from_script_tag(show['seatMapUrl'])['SeatMapData']['Rows'][6:]
             for row in rows_i_care_about:
                bool_seats=[bool(int(seat["Status"])) for seat in row['Seats']]
                continuous_seats_free=longest_false_streak(bool_seats)
                show_timestamp = datetime.datetime.fromisoformat(show['showStartDateTime'])
                if continuous_seats_free >=2:
                    print(f'There are {continuous_seats_free} seats in row {row["RowLabel"]} at {show_timestamp}')
                #seat_maps[datetime.datetime(show['showStartDateTime'])]=object