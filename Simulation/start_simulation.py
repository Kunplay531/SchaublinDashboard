from PowerSimulator import PowerSimulator
from EStopSimulator import EStopSimulator
from RPMSimulator import RPMSimulator

async def main():
    # Start the WebSocket server on 0.0.0.0 and port 8080
    async with websockets.serve(RPMSimulator.rpm_sender_random, "0.0.0.0", 8000):
        print("WebSocket server is running on ws://0.0.0.0:8000")
        await asyncio.Future()  # Run forever
        
    async with websockets.serve(EStopSimulator.emergency_stop_simulator, "0.0.0.0", 8002):
        print("WebSocket server is running on ws://0.0.0.0:8002")
        await asyncio.Future()  # Run forever