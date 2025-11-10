from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import json, os

app = Flask(__name__)

# Twilio credentials (will come from Render environment variables)
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TWILIO_NUMBER = "+18332932963"

client = Client(ACCOUNT_SID, AUTH_TOKEN)
ALERT_FILE = "alert_list.json"

def load_list():
    if not os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "w") as f:
            json.dump([], f)
    with open(ALERT_FILE, "r") as f:
        return json.load(f)

def save_list(lst):
    with open(ALERT_FILE, "w") as f:
        json.dump(lst, f)

@app.route("/sms", methods=["POST"])
def sms_reply():
    msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")
    resp = MessagingResponse()
    lst = load_list()
    lower = msg.lower()

    if lower == "yes":
        if sender not in lst:
            lst.append(sender)
            save_list(lst)
            resp.message(f"✅ {sender} added to the alert list.")
        else:
            resp.message("You're already on the alert list.")
    elif lower.startswith("add"):
        num = msg[3:].strip()
        if not num.startswith("+"):
            num = "+1" + num
        if num not in lst:
            lst.append(num)
            save_list(lst)
            resp.message(f"✅ {num} added to the alert list.")
        else:
            resp.message(f"{num} is already on the alert list.")
    elif lower.startswith("remove"):
        num = msg[6:].strip()
        if not num.startswith("+"):
            num = "+1" + num
        if num in lst:
            lst.remove(num)
            save_list(lst)
            resp.message(f"🗑️ {num} removed from the alert list.")
        else:
            resp.message(f"{num} not found.")
    elif lower == "list":
        if lst:
            resp.message("📋 Alert List:\n" + "\n".join(lst))
        else:
            resp.message("The alert list is currently empty.")
    elif lower.startswith("send "):
        message_body = msg[5:].strip()
        for number in lst:
            client.messages.create(
                to=number,
                from_=TWILIO_NUMBER,
                body=message_body
            )
        resp.message("✅ Broadcast sent to all numbers on the list.")
    else:
        resp.message("Commands: yes | add[number] | remove[number] | list | send [message]")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
