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

Look at every closure, 
if it matches my route, 
If yes, report that 
'''


import os
import requests
import html
import re
from requests.exceptions import ConnectionError, HTTPError, Timeout, RequestException
# requests allows you to visit websites from code / internet requests
# furthermore, import errors to handle errors



TRANSTAR_LANE_CLOSURE_URL = "https://traffic.houstontranstar.org/construction/construction_report_media.aspx"
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}" if NTFY_TOPIC else None

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


def extract_relevant_closure_snippets(page_text):
    """
    Takes raw TranStar HTML text.
    Converts it into readable text.
    Returns text snippets that mention one of our route keywords.
    """
    text = re.sub(r"<[^>]+>", " ", page_text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()

    relevant_snippets = []
    lowercase_text = text.lower()

    for keyword in KEYWORDS:
        start_index = lowercase_text.find(keyword)

        while start_index != -1:
            snippet_start = max(start_index - 250, 0)
            snippet_end = min(start_index + 500, len(text))
            snippet = text[snippet_start:snippet_end].strip()

            relevant_snippets.append(
                {
                    "matched_keyword": keyword,
                    "snippet": snippet,
                }
            )

            start_index = lowercase_text.find(keyword, start_index + len(keyword))

    return relevant_snippets


def get_transtar_closures():
    """
    Calls the public Houston TranStar construction report page.
    Returns closure snippets that mention our route keywords.
    If the website cannot be reached, returns an empty list instead of crashing.
    """
    try:
        response = requests.get(TRANSTAR_LANE_CLOSURE_URL, timeout=10)
        response.raise_for_status()
        return extract_relevant_closure_snippets(response.text)

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


def send_phone_notification(message):
    """
    Sends a push notification to your phone through ntfy.
    """
    if not NTFY_URL:
        print("NTFY_TOPIC is missing. Notification was not sent.")
        return

    try:
        response = requests.post(
            NTFY_URL,
            data=message.encode("utf-8"),
            headers={
                "Title": "Allen Parkway Alert",
                "Priority": "high",
            },
            timeout=10,
        )
        response.raise_for_status()
        print("Phone notification sent.")
    except ConnectionError:
        print("Could not connect to ntfy.")
        print("Notification was not sent because of a network/DNS issue.")
    except Timeout:
        print("ntfy took too long to respond.")
    except HTTPError as error:
        print(f"ntfy returned an HTTP error: {error}")
    except RequestException as error:
        print(f"Unexpected notification error: {error}")


def main():
    closures = get_transtar_closures()

    matching_closures = []

    for closure in closures:
        if closure_matches_route(closure):
            matching_closures.append(closure)

    if matching_closures:
        alert_message = "Allen Parkway-related closure detected. Take Exit 47D instead."

        print("Allen Parkway-related closure detected.")
        print("Recommendation: take Exit 47D instead.")
        print()
        print("Matching closures:")
        for closure in matching_closures:
            print(closure)
            print("-" * 80)

        send_phone_notification(alert_message)
    else:
        print("No Allen Parkway-related closures found right now.")


if __name__ == "__main__":
    main()