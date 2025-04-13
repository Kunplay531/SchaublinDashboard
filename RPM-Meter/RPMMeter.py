import time
import RPi.GPIO as GPIO
import asyncio
import statistics

gpio_pin = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

last_pulse_time = None
rpm_value = 0

# Define threshold: max allowed % change between measurements
MAX_CHANGE_PERCENT = 10  # Allow ±30% change

def is_outlier(new_value, reference):
    global last_outliers
    last_outliers.append(new_value)
    if reference == 0:
        return False
    if len(last_outliers) > 5:
        change = abs(statistics.median(last_outliers)) / reference * 100
        if change > MAX_CHANGE_PERCENT:
            return True
    change = abs(new_value - reference) / reference * 100
    return change > MAX_CHANGE_PERCENT

def pulse_detected(channel):
    global last_pulse_time, rpm_value
    current_time = time.monotonic()

    if last_pulse_time is not None:
        elapsed_time = current_time - last_pulse_time
        if elapsed_time > 0:
            new_rpm = (1 / elapsed_time) * 60

            # Filter out sudden spikes
            if not is_outlier(new_rpm, rpm_value):
                rpm_value = new_rpm

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
