import psutil
import ssl
import socket
import utils
import time
import logger

def pollEvents(pollObject):

  while True:

    for fd, event in pollObject.poll():
      yield fd, event

def serverEvents(broadcastSocket, ca, mutableSocket):
  
  while True:

      data, serverAddress = broadcastSocket.recvfrom(65000)
      port = utils.getServerPort(data)

      if port == -1:
        continue

      purpose = ssl.Purpose.SERVER_AUTH
      context = ssl.create_default_context(purpose=purpose, cafile=ca)

      rawServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

      try:
        rawServerSocket.connect((serverAddress[0], port))
        tmpSecureSocket = context.wrap_socket(rawServerSocket, server_hostname="Lab-Monitor")
        mutableSocket.setSocket(tmpSecureSocket)
      
      except:      
        continue
      
def USBEvents(serverSocket):

  oldDevices = psutil.disk_partitions()
  logger.log("Listening to partition mount events", serverSocket)

  while True:

    newDevices = psutil.disk_partitions()

    if(len(newDevices) > len(oldDevices)):
      logger.log("New Partition Mounted", serverSocket)

    elif(len(newDevices) < len(oldDevices)):
      logger.log("Partition Unmounted", serverSocket)

    oldDevices = newDevices
    time.sleep(0.5)

def networkEvents(serverSocket):
  logger.log("Listening to network events", serverSocket)
