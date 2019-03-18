import socket
import events
from threading import Thread

PORT = 12345

broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.bind(('', PORT))

while True:

  data, serverAddress = broadcastSocket.recvfrom(65000)
  message = data.decode("ascii")

  if len(message.split("@")) == 2 and message.split("@")[0] == "server-init" :
    print("Received server init: ", data.decode("ascii"), serverAddress[0])
    break

broadcastSocket.close()

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.connect((serverAddress[0], int(message.split("@")[1])))

# serverSocket.sendall(b"hello server !!!!~")
Thread(target=events.networkEvents, args=[serverSocket]).start()
Thread(target=events.USBEvents, args=[serverSocket]).start()

while True:
  pass