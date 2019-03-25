import argparse
import events
import socket
import utils
import events

from multiprocessing import Process

parser = argparse.ArgumentParser(description='Lab-Monitor Server')
parser.add_argument("-p", "--port", help="Port Number", type=int, default=45001)
args = parser.parse_args()
PORT = args.port

broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.bind(('', PORT))

listeningToEvents = False
usbProcess = None
networkProcess = None

while True:

    data, serverAddress = broadcastSocket.recvfrom(65000)
    message = utils.decrypt(data)

    if(message == "NA"):
      print(f"Invalid message received from {serverAddress}")
      continue

    if message == "server-stop" and listeningToEvents:

      print(f"Received server-stop from {serverAddress}")
      listeningToEvents = False
      usbProcess.terminate()
      networkProcess.terminate()
      usbProcess = None
      networkProcess = None
      continue

    serverPort = utils.getServerPort(message)

    if serverPort == -1:
      print(f"Invalid port number received from {serverAddress}")
      continue

    print(f"Received server-init from {serverAddress}")

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:

      serverSocket.connect((serverAddress[0], serverPort))

      if listeningToEvents:
        usbProcess.terminate()
        networkProcess.terminate()

      listeningToEvents = True

      usbProcess = Process(target=events.USBEvents, args=(serverSocket, ))
      networkProcess = Process(target=events.networkEvents, args=(serverSocket, ))
      usbProcess.start()
      networkProcess.start()
    
    except:
      print("Could not connect to the server")  
      continue
