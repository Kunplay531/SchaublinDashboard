import asyncio
import websockets
import random

async def rpm_sender_random(websocket):
    print("Sending random values between 250 and 3000 every second. Press Ctrl+C to stop.")
    try:
        while True:
            random_value = str(random.randint(250, 3000))
            await websocket.send(random_value)
            print(f"Sent random value: {random_value}")
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopped sending random values.")

async def rpm_sender(websocket):
    print("Client connected. Start entering RPM values.")
    try:
        while True:
            # Take RPM input from the keyboard
            rpm_value = input("Enter RPM value to send: ")
            # Send the RPM value to the WebSocket client
            await websocket.send(rpm_value)
            print(f"Sent RPM value: {rpm_value}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")

async def main():
    # Start the WebSocket server on 0.0.0.0 and port 8080
    async with websockets.serve(rpm_sender_random, "0.0.0.0", 8000):
        print("WebSocket server is running on ws://0.0.0.0:8000")
        await asyncio.Future()  # Run forever

# Run the server
asyncio.run(main())
