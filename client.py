import socket
import ssl
import events
from threading import Thread

PORT = 12345
CAFILE = "./keys/CA/ca.crt"

broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.bind(('', PORT))

while True:

  data, serverAddress = broadcastSocket.recvfrom(65000)
  message = data.decode("ascii")

  if len(message.split("@")) == 2 and message.split("@")[0] == "server-init" :
    print("Received server init: ", data.decode("ascii"), serverAddress[0])
    break

broadcastSocket.close()

purpose = ssl.Purpose.SERVER_AUTH
context = ssl.create_default_context(purpose=purpose, cafile=CAFILE)

rawServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rawServerSocket.connect((serverAddress[0], int(message.split("@")[1])))
sslServerSocket = context.wrap_socket(rawServerSocket, server_hostname="Lab-Monitor")

Thread(target=events.networkEvents, args=[sslServerSocket]).start()
Thread(target=events.USBEvents, args=[sslServerSocket]).start()
