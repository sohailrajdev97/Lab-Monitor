import socket
import select
import events
from simplecrypt import encrypt

CLIENT_PORT = 12345
SERVER_PORT = 50000

f = open("./key", "r")
key = f.read()
f.close()

INIT_MESSAGE = encrypt(key, f"server-init@{SERVER_PORT}")

# Send a broadcast to all clients (on the same subnet)
broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broadcastSocket.sendto(INIT_MESSAGE, ('', CLIENT_PORT))
broadcastSocket.close()

# Create a socket for accepting incoming TCP connections from clients
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(('', SERVER_PORT))
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
