import time
import RPi.GPIO as GPIO
import asyncio
import statistics

gpio_pin = 27
TIMEOUT_DURATION = 2  # seconds without pulse before resetting RPM

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

last_pulse_time = time.monotonic()
rpm_value = 0
values = []


def pulse_detected(channel):
    global last_pulse_time, rpm_value, values
    current_time = time.monotonic()

    if last_pulse_time is not None:
        elapsed_time = current_time - last_pulse_time
        if elapsed_time > 0:
            new_rpm = (1 / elapsed_time) * 60

            if len(values) > 5:
                values.append(new_rpm)
                rpm_value = statistics.median(values)
                values = []
            else:
                values.append(new_rpm)

    last_pulse_time = current_time


GPIO.add_event_detect(gpio_pin, GPIO.RISING, callback=pulse_detected, bouncetime=15)


async def main():
    global rpm_value
    while True:
        current_time = time.monotonic()
        if current_time - last_pulse_time > TIMEOUT_DURATION:
            rpm_value = 0
            values.clear()  # optional: clear old data when idle

        print(f"RPM: {rpm_value:.2f}")
        await asyncio.sleep(1)  # Update every second

asyncio.run(main())
