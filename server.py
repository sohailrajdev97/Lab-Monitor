import socket
import select
import events
from threading import Thread
from simplecrypt import encrypt

CLIENT_PORT = 65000
SERVER_PORT = 50000

# Read the AES key
f = open("./key", "r")
key = f.read()
f.close()

def sendInitMessage(clientPort, serverPort):
  INIT_MESSAGE = encrypt(key, f"server-init@{serverPort}")
  broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  broadcastSocket.sendto(INIT_MESSAGE, ('', clientPort))
  broadcastSocket.close()

def sendStoptMessage(clientPort):
  STOP_MESSAGE = encrypt(key, "server-stop")
  broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  broadcastSocket.sendto(STOP_MESSAGE, ('', clientPort))
  broadcastSocket.close()

def server(serverPort):
  # Create a socket for accepting incoming TCP connections from clients
  serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  serverSocket.bind(('', serverPort))
  serverSocket.listen()

  # Define data structures for async IO
  clientSockets = { serverSocket.fileno(): serverSocket }
  addresses = { }
  bytesReceived = { }

  # Create poll object and register the listening socket
  pollObject = select.poll()
  pollObject.register(serverSocket, select.POLLIN) 

  for fd, event in events.pollEvents(pollObject):
    sock = clientSockets[fd]

    if event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):

      # Client socket is closed
      address = addresses.pop(sock)
      pendingData = bytesReceived.pop(sock, b'').decode("utf8")

      if pendingData:
        print(f"ABNORMAL DISCONNECTION: Client {address} with pending data: {pendingData}")
      else:
        print(f"Disconnection: Client {address}")
      
      pollObject.unregister(fd)
      del clientSockets[fd]
    
    elif sock is serverSocket:

      # New Connection
      sock, address = sock.accept()

      print(f"New Connection from {address}")
      sock.setblocking(False)
      clientSockets[sock.fileno()] = sock
      addresses[sock] = address
      pollObject.register(sock, select.POLLIN)
    
    elif event & select.POLLIN:

      # Incoming data
      nextData = sock.recv(4096)

      if not nextData:
        sock.close()
        continue
      
      totalData = bytesReceived.pop(sock, b'') + nextData

      if(totalData.endswith(b'~')):
        print(f"{addresses[sock][0]}: {totalData.decode('utf8')[:-1]}", end="")

      else:
        bytesReceived[sock] = totalData

if __name__ == "__main__":
  sendInitMessage(CLIENT_PORT, SERVER_PORT)
  Thread(target=server, args=(SERVER_PORT, )).start()
