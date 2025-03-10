import asyncio
import websockets
import time
import gpiod

# Definiere den GPIO-Pin (Pin 27)
gpio_pin = 27

# Verwende gpiochip0, um auf GPIO 27 zuzugreifen
chip = gpiod.Chip('gpiochip0')  # gpiochip0 ist der Standard-GPIO-Controller
line = chip.get_line(gpio_pin)  # Holen der GPIO-Zeile für Pin 27

# Setze GPIO 27 als Eingang
line.request(consumer="rpm-meter", type=gpiod.LINE_REQ_DIR_IN)

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

# Funktion zum Überwachen des GPIO-Pins und Zählen der HIGH-Pulse
def read_gpio():
    global pulse_count
    value = line.get_value()  # Lese den Wert des GPIO-Pins (0 = LOW, 1 = HIGH)
    if value == 1:  # Wenn der Pin HIGH ist
        pulse_count += 1

async def rpm_sender(websocket):
    print("Client connected. Sending RPM values.")
    try:
        while True:
            read_gpio()  # Überprüfe den GPIO
            calculate_rpm()  # Berechne die RPM
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
