def pollEvents(pollObject):
  while True:
    for fd, event in pollObject.poll():
      yield fd, event

def USBEvents(serverSocket):
  serverSocket.sendall(b"Listening to USB events~")

def networkEvents(serverSocket):
  serverSocket.sendall(b"Listening to Network Events events~")
  pass