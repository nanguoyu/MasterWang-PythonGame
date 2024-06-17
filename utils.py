import socket
import threading

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip
class GameServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.client_socket = None
        self.address = None
        self.running = True
        self.player = None  # Reference to the player object to control
        self.connected = False  # 标志是否已建立连接

    def start(self):
        print(f"Server started on {self.host}:{self.port}")
        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"Connection from {address} has been established!")
                self.client_socket = client_socket
                self.address = address
                self.connected = True  # 设置连接标志
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            except socket.error:
                break

    def handle_client(self, client_socket):
        while self.running:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"[Server]: get {data}")
                self.handle_command(data)
            except socket.error:
                break
        client_socket.close()

    def handle_command(self, command):
        # 重置所有移动状态
        self.player.moving_right = False
        self.player.moving_left = False

        if command == "Right":
            self.player.moving_right = True
        elif command == "Left":
            self.player.moving_left = True
        elif command == "Jump":
            if not self.player.jumping:
                self.player.jumping = True
                self.player.on_ground = False
                self.player.vel_y = -10
        elif command == "Attack":
            if not self.player.attacking:
                self.player.attacking = True

    def stop(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        self.server_socket.close()
