import asyncio
import websockets
import time
import RPi.GPIO as GPIO

# Definiere den GPIO-Pin (Pin 27)
gpio_pin = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Variablen zur Berechnung der RPM
last_time = time.time()
pulse_count = 0
rpm_value = 0

# Funktion zur Verarbeitung der Pulsflanken (Interrupt)
def pulse_detected(channel):
    global pulse_count
    pulse_count += 1  # Jede steigende Flanke als Puls zählen

# GPIO Interrupt auf steigende Flanken setzen
GPIO.add_event_detect(gpio_pin, GPIO.RISING, callback=pulse_detected, bouncetime=2)  # 2 ms debounce

# Funktion zur Berechnung der RPM
def calculate_rpm():
    global pulse_count, rpm_value, last_time
    current_time = time.time()
    elapsed_time = current_time - last_time

    if elapsed_time >= 1:  # Alle 1 Sekunde RPM berechnen
        rpm_value = (pulse_count / elapsed_time) * 60
        pulse_count = 0
        last_time = current_time

async def rpm_sender(websocket):
    print("Client connected. Sending RPM values.")
    try:
        while True:
            calculate_rpm()
            await websocket.send(str(rpm_value))
            await asyncio.sleep(0.1)  # 10 Hz Update-Rate
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")

async def main():
    async with websockets.serve(rpm_sender, "0.0.0.0", 8000):
        print("WebSocket server is running on ws://0.0.0.0:8000")
        await asyncio.Future()  # Server läuft für immer

asyncio.run(main())
