# First version
# Checks for closure by: 
'''
Searching for allen Parkway related words 
print a warning if found

Use Houston TranStar because lane closures are upadted here by the minute. 

Explanations: 
requests.get(...): Goes into the TranStar closure feed 
response.json(...): Turns the feed into Python Data 
KEYWORDS: streets keywords we are checking for closures 
closure_matches_route(...): Checks one closure and asks if this mentions anything near allenparkway
'''


import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout, RequestException
# requests allows you to visit websites from code / internet requests
# furthermore, import errors to handle errors

TRANSTAR_LANE_CLOSURE_URL = "https://traffic.houstontranstar.org/datafeed/closures_json.aspx"

# provide a list of keywords to look for in the website regarding closures
KEYWORDS = [
    "allen parkway",
    "allen pkwy",
    "bagby",
    "waugh",
    "montrose",
    "taft",
    "sabine",
    "memorial drive",
    "exit ramp to allen parkway",
]


def closure_matches_route(closure):
    """
    Takes one closure item from TranStar.
    Turns the whole closure into lowercase text.
    Checks whether any Allen Parkway-related keyword appears.
    """
    closure_text = str(closure).lower()

    for keyword in KEYWORDS:
        if keyword in closure_text:
            return True

    return False


def get_transtar_closures():
    """
    Calls Houston TranStar's closure feed.
    Returns the JSON data.
    If the website cannot be reached, returns an empty list instead of crashing.
    """
    try:
        response = requests.get(TRANSTAR_LANE_CLOSURE_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except ConnectionError:
        print("Could not connect to Houston TranStar.")
        print("Most likely issue: DNS/network problem, Wi-Fi issue, or the site is temporarily unreachable.")
        return []
    except Timeout:
        print("Houston TranStar took too long to respond.")
        return []
    except HTTPError as error:
        print(f"Houston TranStar returned an HTTP error: {error}")
        return []
    except RequestException as error:
        print(f"Unexpected request error: {error}")
        return []


def main():
    closures = get_transtar_closures()

    matching_closures = []

    for closure in closures:
        if closure_matches_route(closure):
            matching_closures.append(closure)

    if matching_closures:
        print("Allen Parkway-related closure detected.")
        print("Recommendation: take Exit 47D instead.")
        print()
        print("Matching closures:")
        for closure in matching_closures:
            print(closure)
            print("-" * 80)
    else:
        print("No Allen Parkway-related closures found right now.")


if __name__ == "__main__":
    main()