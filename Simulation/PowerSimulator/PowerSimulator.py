import asyncio
import websockets
import random

async def power_sender_random(websocket):
    print("Sending random values between 1 and 100 every second. Press Ctrl+C to stop.")
    try:
        while True:
            random_value = str(random.randint(1, 100))
            await websocket.send(random_value)
            print(f"Sent random value: {random_value}")
            await asyncio.sleep(5)
    except KeyboardInterrupt:
        print("Stopped sending random values.")

async def power_sender(websocket):
    print("Client connected. Start entering RPM values.")
    try:
        while True:
            # Take power input from the keyboard
            power_value = input("Enter power percentage value to send: ")
            # Send the power value to the WebSocket client
            await websocket.send(power_value)
            print(f"Sent RPM value: {power_value}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")

async def main():
    # Start the WebSocket server on specific ip and port 8001
    async with websockets.serve(power_sender_random, "0.0.0.0", 8001):
        print("WebSocket server is running on ws://0.0.0.0:8001")
        await asyncio.Future()  # Run forever

# Run the server
asyncio.run(main())
