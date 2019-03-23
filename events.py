import logger
import psutil
import socket
import subprocess
import time
import utils

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
  hostname = socket.gethostname()    
  ip = socket.gethostbyname(hostname)

  dumpFilter = f"ip and host {ip} and port not 53 and ((tcp[tcpflags] & tcp-syn != 0) or udp)"
  dumpProcess = subprocess.Popen(("tcpdump", "-l", "-nn", dumpFilter), stdout=subprocess.PIPE)

  for row in iter(dumpProcess.stdout.readline, b''):

    log = row.decode("utf8")
    tokenisedLog = log.split()

    src = tokenisedLog[2]
    dest = tokenisedLog[4].rstrip(":")

    try:
      srcService = socket.getservbyport(int(src.split(".")[-1]))
      src = f"{srcService.upper()} {'.'.join(src.split('.')[0:-1])}" 
    except:
      split = src.split(".")
      src = ".".join(split[0:-1]) + ":" + split[-1]
    
    try:
      destService = socket.getservbyport(int(dest.split(".")[-1]))
      dest = f"{destService.upper()} {'.'.join(dest.split('.')[0:-1])}" 
    except:
      split = src.split(".")
      src = ".".join(split[0:-1]) + ":" + split[-1]
      
    logger.log(f"{src} --> {dest}", serverSocket)
