import socket
import select
import ssl
import events

CLIENT_PORT = 12345
SERVER_PORT = 50000
CAFILE = "./keys/CA/ca.crt"
PEMFILE = "./keys/server.pem"
INIT_MESSAGE = f"server-init@{SERVER_PORT}"

# Send a broadcast to all clients (on the same subnet)
broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broadcastSocket.sendto(INIT_MESSAGE.encode("ascii"), ('', CLIENT_PORT))
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
    pendingData = bytesReceived.pop(sock, b'').decode("ascii")

    if pendingData:
      print(f"ABNORMAL DISCONNECTION: Client {address} with pending data: {pendingData}")
    else:
      print(f"Disconnection: Client {address}")
    
    pollObject.unregister(fd)
    del clientSockets[fd]
  
  elif sock is serverSocket:

    # New Connection

    # Setup TLS
    purpose = ssl.Purpose.CLIENT_AUTH
    context = ssl.create_default_context(purpose=purpose, cafile=CAFILE)
    context.load_cert_chain(PEMFILE)

    # Accept incoming connection
    sock, address = sock.accept()
    sock = context.wrap_socket(sock, server_side=True)

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
      print(f"{addresses[sock][0]}: {totalData.decode('ascii')[:-1]}", end="")

    else:
      bytesReceived[sock] = totalData
