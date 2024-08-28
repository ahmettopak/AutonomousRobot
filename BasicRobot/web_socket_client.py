<<<<<<< HEAD
import asyncio
import websockets
=======
from websocket import create_connection, WebSocketException

from websocket import create_connection, WebSocketException
import time
>>>>>>> a0de270 (Web Socket exception handled)

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
<<<<<<< HEAD

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
=======
        self.websocket = None
        self.is_connected = False

    def connect(self):
        if not self.is_connected:
            try:
                self.websocket = create_connection(self.uri, timeout=10)  # Timeout ekledik
                self.is_connected = True
                print("WebSocket bağlantısı kuruldu.")
            except WebSocketException as e:
                print(f"WebSocket bağlantısı kurulurken bir hata oluştu: {e}")
                self.is_connected = False
            except ConnectionRefusedError as e:
                print(f"Bağlantı reddedildi: {e}")
                self.is_connected = False
            except Exception as e:
                print(f"Beklenmeyen bir hata oluştu: {e}")
                self.is_connected = False

    def send_data(self, data):
        if not self.is_connected:
            self.connect()
        if self.is_connected:
            try:
                self.websocket.send(data)
            except WebSocketException as e:
                print(f"Veri gönderilirken bir hata oluştu: {e}")
                self.close()  # Bağlantıyı kapat
                # Hatanın detaylarını anlamak için daha fazla bilgi ekleyin
                print(f"Hata ayrıntısı: {e}")
            except Exception as e:
                print(f"Beklenmeyen bir hata oluştu: {e}")
                self.close()  # Bağlantıyı kapat
                # Hatanın detaylarını anlamak için daha fazla bilgi ekleyin
                print(f"Hata ayrıntısı: {e}")

    def receive_data(self):
        if not self.is_connected:
            self.connect()
        if self.is_connected:
            try:
                response = self.websocket.recv()
                return response
            except WebSocketException as e:
                print(f"Veri alınırken bir hata oluştu: {e}")
                self.close()
                return None

    def close(self):
        if self.is_connected:
            try:
                self.websocket.close()
                self.is_connected = False
                print("WebSocket bağlantısı kapatıldı.")
            except WebSocketException as e:
                print(f"WebSocket bağlantısı kapatılırken bir hata oluştu: {e}")


# # Örnek kullanım:
# try:
#     client = WebSocketClient("ws://example.com/socket")  # URI'yi doğru olduğundan emin olun
#     client.send_data("Merhaba, dünya!")
#     response = client.receive_data()
#     if response:
#         print(response)
#     else:
#         print("Veri alınamadı.")
# except WebSocketException as e:
#     print(f"WebSocket ile ilgili bir hata oluştu: {e}")
# finally:
#     client.close()
>>>>>>> a0de270 (Web Socket exception handled)
