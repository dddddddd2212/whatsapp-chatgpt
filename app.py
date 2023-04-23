import asyncio
import logging
import os
from asyncio import new_event_loop, set_event_loop
from concurrent.futures import ThreadPoolExecutor

import openai
from dotenv import load_dotenv
from flask import Flask, request
from twilio.rest import Client

load_dotenv()

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]
YOUR_PHONE_NUMBER = os.environ["YOUR_PHONE_NUMBER"]

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = Flask(__name__)

CHATGPT_API_URL = "https://api.openai.com/v1/chat/completions"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_response(prompt: str) -> str:
    """
    Generate a response using ChatGPT API.

    :param prompt: The input message to generate a response for.
    :return: The generated response as a string.
    """
    openai.api_key = OPENAI_API_KEY

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1600,
        )
        generated_message = completion.choices[0].message["content"]
        print(generated_message)
        return generated_message.strip()

    except Exception as e:
        app.logger.error(f"Failed to send request to ChatGPT API: {e}")
        return "I'm sorry, but I'm unable to generate a response at the moment."


async def process_whatsapp_message(incoming_msg: str) -> None:
    """
    Process the incoming WhatsApp message asynchronously.

    :param incoming_msg: The incoming message to process.
    """
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor() as pool:
        chatgpt_response = await loop.run_in_executor(
            pool, generate_response, incoming_msg
        )

    try:
        twilio_client.messages.create(
            body=chatgpt_response,
            from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
            to=f"whatsapp:{YOUR_PHONE_NUMBER}",
        )
        logger.info("Message sent to WhatsApp successfully.")
    except Exception as e:
        logger.error(f"Failed to send message via Twilio: {e}")


@app.route("/whatsapp", methods=["POST"])
def whatsapp_message():
    """
    Handle incoming WhatsApp messages and process them asynchronously.

    :return: A response indicating that message processing has been initiated.
    """
    incoming_msg = request.values.get("Body", "").strip()

    loop = new_event_loop()
    set_event_loop(loop)
    loop.run_until_complete(process_whatsapp_message(incoming_msg))

    return "Message processing initiated", 202


if __name__ == "__main__":
    app.run(debug=True)
