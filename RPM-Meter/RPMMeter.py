import asyncio
# import websockets
import time
import statistics
import RPi.GPIO as GPIO

gpio_pin = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

last_pulse_time = None
rpm_measurements = []
rpm_value = 0

def pulse_detected(channel):
    global last_pulse_time, rpm_value, rpm_measurements
    current_time = time.monotonic()

    if last_pulse_time is not None:
        elapsed_time = current_time - last_pulse_time
        if elapsed_time > 0:
            new_rpm = (1 / elapsed_time) * 60
            rpm_measurements.append(new_rpm)

            # Keep only the last 5 measurements
            if len(rpm_measurements) > 5:
                rpm_measurements.pop(0)

            # Update rpm_value to the median of the last 5
            rpm_value = statistics.median(rpm_measurements)

    last_pulse_time = current_time

GPIO.add_event_detect(gpio_pin, GPIO.RISING, callback=pulse_detected, bouncetime=15)

# async def rpm_sender(websocket):
#     print("Client connected. Sending RPM values.")
#     try:
#         while True:
#             await websocket.send(str(rpm_value))
#             await asyncio.sleep(0.1)  # Send updates every 100 ms
#     except websockets.exceptions.ConnectionClosed:
#         print("Client disconnected.")

async def main():
    # async with websockets.serve(rpm_sender, "0.0.0.0", 8000):
    #     print("WebSocket server is running on ws://0.0.0.0:8000")
    #     await asyncio.Future()  # Server läuft für imme
    
    
    while True:
        print(f"RPM: {rpm_value:.2f}")
        await asyncio.sleep(1)  # Update every second   

asyncio.run(main())
