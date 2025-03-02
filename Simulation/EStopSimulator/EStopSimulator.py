import asyncio
import websockets

async def emergency_stop_simulator(websocket):
    print("Client connected. Press 'e' for emergency stop (1) and 'c' to reset (0).")
    try:
        while True:
            key = input("Press 'e' for stop, 'c' to reset: ")
            if key == 'e':
                await websocket.send("1")
                print("Sent: 1 (Emergency Stop)")
            elif key == 'c':
                await websocket.send("0")
                print("Sent: 0 (Reset)")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")

async def main():
    async with websockets.serve(emergency_stop_simulator, "0.0.0.0", 8002):
        print("WebSocket server is running on ws://0.0.0.0:8002")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
