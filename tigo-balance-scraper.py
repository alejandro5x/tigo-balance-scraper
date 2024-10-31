import re
from playwright.sync_api import Playwright, sync_playwright, expect, TimeoutError
from dotenv import load_dotenv
from datetime import datetime
import time
import paho.mqtt.client as mqtt
import os
import json
from bs4 import BeautifulSoup

load_dotenv()
tigo_account = os.getenv('TIGO_NUMBER')
tigo_password = os.getenv('TIGO_PASSWORD')
mqtt_user = os.getenv('MQTT_USER')
mqtt_password = os.getenv('MQTT_PASSWORD')
mqtt_server = os.getenv('MQTT_BROKER')
mqtt_port = int(os.getenv('MQTT_PORT'))
mqtt_topic = os.getenv('TIGO_MQTT_TOPIC')
mqtt_error_topic = os.getenv('TIGO_MQTT_ERROR_TOPIC')  # Separate Topic for errors

def run(playwright: Playwright) -> None:

    #browser = playwright.chromium.launch(headless=False, slow_mo=50)
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://mi.tigo.com.pa/ingresar")

    try:
        page.locator("button").filter(has_text=re.compile(r"^Ingresar$")).click()
        page.get_by_label("Correo electrónico").fill(tigo_account)
        page.get_by_role("button", name="CONTRASEÑA CONTRASEÑA").click()
        page.get_by_role("textbox").fill(tigo_password)
        page.get_by_role("button", name="Continuar").click()

        page.wait_for_timeout(9000)
        # Getting balance
        balance_element = page.get_by_label("billAmount").inner_text()
        balance = balance_element.replace("B/. ", "")
        print(balance)

        page.get_by_label("openDrawerWebTopHeader").get_by_role("img").nth(1).click()
        page.get_by_text("CERRAR SESIÓN").click()
        send_mqtt_data(mqtt_server, mqtt_port, mqtt_user, mqtt_password, mqtt_topic, balance)
        send_mqtt_error(mqtt_server, mqtt_port, mqtt_user, mqtt_password, mqtt_error_topic, "")
    except (TimeoutError, ValueError) as e:
        error_message = f"Error getting balance: {str(e)}"
        print(error_message)
        send_mqtt_error(mqtt_server, mqtt_port, mqtt_user, mqtt_password, mqtt_error_topic, error_message)
        balance = "Error"
    finally:
        context.close()
        browser.close()


def send_mqtt_data(server, port, user, password, topic, balance):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, mqtt_user)
    client.username_pw_set(user, password)
    client.connect(server, port)
    client.loop_start()

    xpayload = json.dumps({
        "state": str(balance),
        "updated_ts": str(int(time.time())),
        "updated_dt": str(datetime.now())
    }, sort_keys=True, default=str)

    client.publish(topic=topic, payload=xpayload, qos=0, retain=False)
    time.sleep(1)
    client.loop_stop()

def send_mqtt_error(server, port, user, password, topic, error_message):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, mqtt_user)
    client.username_pw_set(user, password)
    client.connect(server, port)
    client.loop_start()

    xpayload = json.dumps({
        "error": error_message,
        "updated_ts": str(int(time.time())),
        "updated_dt": str(datetime.now())
    }, sort_keys=True, default=str)

    client.publish(topic=topic, payload=xpayload, qos=0, retain=False)
    time.sleep(1)
    client.loop_stop()

with sync_playwright() as playwright:
    run(playwright)
