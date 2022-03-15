import calendar
import datetime
import random
import re
import requests
import time
import pytz


DAY_NUMBER = {
    name: num for num, name in enumerate(calendar.day_name)
}

offerings = [
    {
        "offering_guid": "d3ab9dedb9d444f2af5c6848d5cd5bd3",
        "instructor": "Julie",
        "day": "Tuesday",
        "start": "12:00pm",
        "end": "1:00pm",
        "max": 20,
    },
    {
        "offering_guid": "3a9eec849bf149a7a4e4dcc6029dccc2",
        "instructor": "Alicia",
        "day": "Tuesday",
        "start": "5:45pm",
        "end": "6:55pm",
        "max": 20,
    },
    {
        "offering_guid": "7219cf17a8c240e6a0f55a91f1a2961f",
        "instructor": "Bryant",
        "day": "Tuesday",
        "start": "7:30pm",
        "end": "8:40pm",
        "max": 25,
    },
    {
        "offering_guid": "7ca73904c3d9495bac3a94aa15f8c6df",
        "instructor": "Britany",
        "day": "Wednesday",
        "start": "7:15pm",
        "end": "8:25pm",
        "max": 20,
    },
    {
        "offering_guid": "bdd150c8804a4849b8cf9c8e0c28f785",
        "instructor": "Julie",
        "day": "Thursday",
        "start": "5:45pm",
        "end": "6:55pm",
        "max": 18,
    },
    {
        "offering_guid": "9fe1cf2b9bd94d5db616ed53459cca8e",
        "instructor": "Laura",
        "day": "Wednesday",
        "start": "5:45pm",
        "end": "6:55pm",
        "max": 18,
    },
    {
        "offering_guid": "07c0e269b1824adf90e259b7cc9b6859",
        "instructor": "Aly",
        "day": "Thursday",
        "start": "7:15pm",
        "end": "8:45pm",
        "max": 21,
    }
]

def request_offering_data(offering):
    cookies = {
        'BrowserSessionId': '622ff322876e1',
        'RGPPortalSessionID': 'oghon1q17bfs5qajmgjkjfmgm7',
        'RGPSessionGUID': '1145a158d3c68c277f666bbfd151ad221c0931335529a85fb5630c7cfbe51ad76492c961aaf71834051d91218b3ca347',
        'AWSELB': 'A5EDC1071EB54DEE085FA9BC53DB5910EF75B9C87FEA9FBE239F1F1B88F39F8F8C70049A401FD2B5F786A06FD97C8DB4A7C8A93282A9197AABB39E4BFACEB2E7B779767E2C',
        'AWSELBCORS': 'A5EDC1071EB54DEE085FA9BC53DB5910EF75B9C87FEA9FBE239F1F1B88F39F8F8C70049A401FD2B5F786A06FD97C8DB4A7C8A93282A9197AABB39E4BFACEB2E7B779767E2C',
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://app.rockgympro.com',
        'Referer': 'https://app.rockgympro.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }

    params = (
        ('a', 'equery'),
    )

    weekday = DAY_NUMBER[offering['day']]
    today = datetime.datetime.now(pytz.timezone('US/Pacific'))
    next_offering_date = today + datetime.timedelta(days=((today.weekday() + weekday) % 7))

    data = {
        'PreventChromeAutocomplete': '',
        'fctrl_1': 'offering_guid',
        'offering_guid': offering["offering_guid"],
        'fctrl_4': 'show_date',
        'show_date': next_offering_date.strftime("%Y-%m-%d"),
        'ftagname_0_pcount-pid-1-3353458': 'pcount',
        'ftagval_0_pcount-pid-1-3353458': '1',
        'ftagname_1_pcount-pid-1-3353458': 'pid',
        'ftagval_1_pcount-pid-1-3353458': '3353458',
        'fctrl_5': 'pcount-pid-1-3353458',
        'pcount-pid-1-3353458': offering["max"],
    }

    response = requests.post('https://app.rockgympro.com/b/widget/', headers=headers, params=params, cookies=cookies, data=data)
    print(response)
    response = response.json()
    print (response)

    # look for string "no available times" in response["event_list_html"]
    if "NOT AVAILABLE YET" in response["event_list_html"]:
        return offering['max']
    elif "no available times" in response["event_list_html"]:
        # No offering on this day
        raise Exception("No offering on this day")
    elif "Full." in response["event_list_html"]:
        # Class is Full
        return 0
    elif "requested {} space(s), but only".format(offering['max']) in response["event_list_html"]:
        match = re.search(r'but only (\d+) space', response["event_list_html"])
        return int(match.group(1))
    else:
        return offering['max']

for offering in offerings:
    try:
        spots_remaining = request_offering_data(offering)
        # write results to file with timestamp
        with open('results.csv', 'a') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write("{},{},{},{}\n".format(timestamp, offering['offering_guid'], offering['instructor'], spots_remaining))
        print()
    except Exception as e:
        # write error to file with timestamp
        with open('errors.csv', 'a') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write("{},{},{},{}\n".format(timestamp, offering['offering_guid'], offering['instructor'], str(e)))

    # sleep for a random amount of time between 1 and 5 seconds
    sleeptime = random.randint(1, 5)
    time.sleep(sleeptime)
    print("Sleeping for {} seconds".format(sleeptime))