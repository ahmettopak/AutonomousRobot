import asyncio
import websockets

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)

    async def send_data(self, data):
        if not hasattr(self, 'websocket'):
            await self.connect()
        await self.websocket.send(data)
        print(f"Veri gönderildi: {data}")

        # Yanıt al (isteğe bağlı)
        response = await self.websocket.recv()
        print(f"Sunucudan yanıt alındı: {response}")

    async def close(self):
        if hasattr(self, 'websocket'):
            await self.websocket.close()
            print("WebSocket bağlantısı kapatıldı.")

# # Kullanım örneği
# async def main():
#     uri = "ws://192.168.1.58:2006"
#     client = WebSocketClient(uri)

#     try:
#         await client.send_data("Merhaba, WebSocket!")
#     finally:
#         await client.close()

# # Asenkron fonksiyonu çalıştır
# asyncio.run(main())
