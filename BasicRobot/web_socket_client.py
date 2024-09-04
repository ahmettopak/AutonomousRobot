from websocket import create_connection, WebSocketException
import time
import select

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.is_connected = False

    def connect(self):
        if not self.is_connected:
            try:
                self.websocket = create_connection(self.uri, timeout=1)  # Timeout arttırıldı
                self.is_connected = True
                print("WebSocket bağlantısı kuruldu.")
            except WebSocketException as e:
                #print(f"WebSocket bağlantısı kurulurken bir hata oluştu: {e}")
                self.is_connected = False
            except ConnectionRefusedError as e:
                #print(f"Bağlantı reddedildi: {e}")
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
                self.close()
                self.connect()
            except Exception as e:
                #print(f"Beklenmeyen bir hata oluştu: {e}")
                self.close()
                self.connect()

    def receive_data(self):
        if not self.is_connected:
            self.connect()
        if self.is_connected:
            try:
                response = self.websocket.recv()

                return response
            
            except WebSocketException as e:
                print(f"Veri alınırken bir hata oluştu: {e}")
                #self.close()
                #self.connect()
                return None
            except Exception as e:
                print(f"Beklenmeyen bir hata oluştu: {e}")
                #self.close()
                #self.connect()
                return None

    def close(self):
        if self.is_connected:
            try:
                self.websocket.close()
                self.is_connected = False
                print("WebSocket bağlantısı kapatıldı.")
            except WebSocketException as e:
                print(f"WebSocket bağlantısı kapatılırken bir hata oluştu: {e}")
            except Exception as e:
                print(f"Beklenmeyen bir hata oluştu: {e}")

    def keep_alive(self, interval=30):
        while self.is_connected:
            try:
                self.websocket.ping()
            except WebSocketException as e:
                print(f"Ping atılırken bir hata oluştu: {e}")
                self.close()
                self.connect()
            time.sleep(interval)
