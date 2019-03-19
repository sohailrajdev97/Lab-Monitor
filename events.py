import psutil
import time

def pollEvents(pollObject):
  while True:
    for fd, event in pollObject.poll():
      yield fd, event

def USBEvents(serverSocket):

  oldDevices = psutil.disk_partitions()
  serverSocket.sendall(b"Listening to partition mount events~")

  while True:    

    newDevices = psutil.disk_partitions()

    if(len(newDevices) > len(oldDevices)):
      serverSocket.sendall(b"New partition mounted~")
    elif(len(newDevices) < len(oldDevices)):
      serverSocket.sendall(b"Partition unmounted~")

    oldDevices = newDevices
    time.sleep(0.5)

def networkEvents(serverSocket):
  serverSocket.sendall(b"Listening to Network Events events~")