"""
WebSocket 서버
실시간 양방향 통신을 위한 서버
"""
import asyncio
import websockets
import json
from typing import Set
from config import WEBSOCKET_PORT

# 연결된 클라이언트 관리
connected_clients: Set[websockets.WebSocketServerProtocol] = set()


async def handle_client(websocket, path):
    """클라이언트 연결 처리"""
    connected_clients.add(websocket)
    print(f"✅ 클라이언트 연결됨 (총 {len(connected_clients)}개)")
    
    try:
        async for message in websocket:
            # 클라이언트로부터 메시지 수신 시 처리
            data = json.loads(message)
            print(f"📩 수신: {data}")
            
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)
        print(f"❌ 클라이언트 연결 해제 (총 {len(connected_clients)}개)")


async def broadcast(message: dict):
    """모든 연결된 클라이언트에 메시지 브로드캐스트"""
    if connected_clients:
        message_str = json.dumps(message)
        await asyncio.gather(
            *[client.send(message_str) for client in connected_clients],
            return_exceptions=True
        )


async def main():
    """WebSocket 서버 시작"""
    print(f"🚀 WebSocket 서버 시작: ws://localhost:{WEBSOCKET_PORT}")
    
    async with websockets.serve(handle_client, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()  # 무한 대기


if __name__ == "__main__":
    asyncio.run(main())
