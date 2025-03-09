import asyncio
import websockets
import RPi.GPIO as GPIO
import time

# Definiere GPIO 27 als Eingang
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN)

# Variablen zur Berechnung der RPM
last_time = time.time()
pulse_count = 0
rpm_value = 0

# Frequenz für die Abtastung (120 Hz)
sampling_interval = 1 / 120  # Zeit pro Abtastung in Sekunden

# Funktion zur Berechnung der RPM
def calculate_rpm():
    global pulse_count, rpm_value, last_time
    current_time = time.time()
    
    # Berechne die Zeitspanne, die vergangen ist
    elapsed_time = current_time - last_time

    # Wenn 1 Sekunde vergangen ist, berechne die RPM
    if elapsed_time >= 1:
        rpm_value = (pulse_count / elapsed_time) * 60  # Umrechnung in RPM
        pulse_count = 0  # Zurücksetzen der Pulszählung
        last_time = current_time
        print(f"Calculated RPM: {rpm_value}")

# Callback-Funktion, die bei jedem HIGH-Signal des Sensors aufgerufen wird
def sensor_callback(channel):
    global pulse_count
    pulse_count += 1

# Setze den Callback für das Abtasten des GPIOs
GPIO.add_event_detect(27, GPIO.RISING, callback=sensor_callback)

async def rpm_sender(websocket):
    print("Client connected. Sending RPM values.")
    try:
        while True:
            calculate_rpm()
            # Sende die berechnete RPM an den WebSocket-Client
            await websocket.send(str(rpm_value))
            print(f"Sent RPM value: {rpm_value}")
            await asyncio.sleep(sampling_interval)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")

async def main():
    # Starte den WebSocket-Server auf Port 8000
    async with websockets.serve(rpm_sender, "0.0.0.0", 8000):
        print("WebSocket server is running on ws://0.0.0.0:8000")
        await asyncio.Future()  # Server läuft für immer

# Starte das Event-Loop
asyncio.run(main())
