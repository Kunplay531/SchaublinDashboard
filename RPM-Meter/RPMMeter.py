import time
import RPi.GPIO as GPIO
import asyncio

gpio_pin = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

last_pulse_time = None
rpm_value = 0.0
alpha = 0.2  # Smoothing factor (0.0 = very stable, 1.0 = very reactive)
outlier_threshold = 2.0  # Reject changes that deviate too much from the current RPM

def pulse_detected(channel):
    global last_pulse_time, rpm_value

    current_time = time.monotonic()

    if last_pulse_time is not None:
        elapsed_time = current_time - last_pulse_time
        if elapsed_time > 0:
            new_rpm = (1 / elapsed_time) * 60

            # Outlier rejection: ignore if too far from current RPM
            if rpm_value > 0 and abs(new_rpm - rpm_value) > outlier_threshold * rpm_value:
                return

            # Weighted moving average
            rpm_value = (alpha * new_rpm) + ((1 - alpha) * rpm_value)
    else:
        # First reading: accept without filtering
        rpm_value = 0

    last_pulse_time = current_time

GPIO.add_event_detect(gpio_pin, GPIO.RISING, callback=pulse_detected, bouncetime=5)

async def main():
    while True:
        print(f"RPM: {rpm_value:.2f}")
        await asyncio.sleep(0.1)

asyncio.run(main())
