import events
import socket
from MutableSocket import MutableSocket
from threading import Thread

PORT = 12345

broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.bind(('', PORT))

serverSocket = MutableSocket()

Thread(target=events.serverEvents, args=[broadcastSocket, serverSocket]).start()
Thread(target=events.networkEvents, args=[serverSocket]).start()
Thread(target=events.USBEvents, args=[serverSocket]).start()
