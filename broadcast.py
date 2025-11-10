from twilio.rest import Client
import json, os

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TWILIO_NUMBER = "+18332932963"
ALERT_FILE = "alert_list.json"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def load_list():
    if not os.path.exists(ALERT_FILE):
        return []
    with open(ALERT_FILE, "r") as f:
        return json.load(f)

def send_broadcast(message):
    numbers = load_list()
    for number in numbers:
        client.messages.create(
            to=number,
            from_=TWILIO_NUMBER,
            body=message
        )
    print("✅ Broadcast sent to all numbers.")

if __name__ == "__main__":
    text = input("Enter message to send: ")
    send_broadcast(text)
