import socket

CLIENT_PORT = 12345
SERVER_PORT = 50000

INIT_MESSAGE = f"server-init@{SERVER_PORT}"

# Send a broadcast to all clients (on the same subnet)
broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broadcastSocket.sendto(INIT_MESSAGE.encode("ascii"), ('', CLIENT_PORT))
broadcastSocket.close()

# Create a socket for accepting incoming TCP connections from clients
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', SERVER_PORT))
serverSocket.listen()

while True:
  sock, address = serverSocket.accept()
  print("Connected to a client ", sock.getpeername())