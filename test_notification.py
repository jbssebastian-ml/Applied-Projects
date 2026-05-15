import requests

NTFY_TOPIC = "seb-allen-parkway-closure-92841"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

message = "Test alert: Allen Parkway closure checker is working."

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

print("Notification sent.")