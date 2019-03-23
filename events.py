import psutil
import socket
import utils
import time
import logger

def pollEvents(pollObject):

  while True:

    for fd, event in pollObject.poll():
      yield fd, event

def serverEvents(broadcastSocket, mutableSocket):
  
  while True:

      data, serverAddress = broadcastSocket.recvfrom(65000)
      port = utils.getServerPort(data)

      if port == -1:
        print("Ignoring connection request from: ", serverAddress)
        continue

      tmpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

      try:
        tmpSocket.connect((serverAddress[0], port))
        mutableSocket.setSocket(tmpSocket)
      
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
