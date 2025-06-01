import os
import logging
import openai
from dotenv import load_dotenv
from flask import Flask, request
from twilio.rest import Client

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
YOUR_PHONE_NUMBER = os.getenv("YOUR_PHONE_NUMBER")

app = Flask(__name__)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get("Body", "").strip()
    logging.info(f"Incoming message: {incoming_msg}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for SOMA Wellness Clinic."},
                {"role": "user", "content": incoming_msg}
            ],
            temperature=0.5,
            max_tokens=1600,
        )
        reply = response.choices[0].message["content"].strip()

        client.messages.create(
            body=reply,
            from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
            to=f"whatsapp:{YOUR_PHONE_NUMBER}"
        )
        logging.info("Reply sent successfully.")
    except Exception as e:
        logging.error(f"Error handling message: {e}")

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
