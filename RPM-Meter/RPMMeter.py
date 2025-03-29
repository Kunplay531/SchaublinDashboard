from gpiozero import Button
import asyncio
import websockets
import time

pin = 27
button = Button(pin)

last_pulse_time = None
rpm_value = 0

def pulse_detected():
    global last_pulse_time, rpm_value
    current_time = time.monotonic()
    if last_pulse_time is not None:
        elapsed_time = current_time - last_pulse_time
        if elapsed_time > 0:
            rpm_value = (1 / elapsed_time) * 60
    last_pulse_time = current_time

button.when_pressed = pulse_detected

async def rpm_sender(websocket):
    print("Client connected. Sending RPM values.")
    try:
        while True:
            await websocket.send(str(rpm_value))
            await asyncio.sleep(0.1)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")

async def main():
    async with websockets.serve(rpm_sender, "0.0.0.0", 8000):
        print("WebSocket server is running on ws://0.0.0.0:8000")
        await asyncio.Future()

asyncio.run(main())
