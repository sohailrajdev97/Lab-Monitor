import socket
import select
import events
from threading import Thread
import tkinter
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

def server(serverPort, logArea):
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
        logArea.insert(tkinter.END, f"ABNORMAL DISCONNECTION: Client {address} with pending data: {pendingData}\n")
      else:
        logArea.insert(tkinter.END, f"Disconnection: Client {address}\n")
      
      pollObject.unregister(fd)
      del clientSockets[fd]
    
    elif sock is serverSocket:

      # New Connection
      sock, address = sock.accept()

      logArea.insert(tkinter.END, f"New Connection from {address}\n")
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
        logArea.insert(tkinter.END, f"{addresses[sock][0]}: {totalData.decode('utf8')[:-1]}")

      else:
        bytesReceived[sock] = totalData

def serverBtnCommand():

  if(serverBtn["text"] == "Start Server"):
    logArea.insert(tkinter.END, "Sending connection request ....\n")
    serverBtn["text"] = "Stop Server"
    sendInitMessage(CLIENT_PORT, SERVER_PORT)
    logArea.insert(tkinter.END, "Connection request sent. Waiting for clients ....\n")
  
  else:
    logArea.insert(tkinter.END, "Sending stop message ....\n")
    serverBtn["text"] = "Start Server"
    sendStoptMessage(CLIENT_PORT)
    logArea.insert(tkinter.END, "Stop message sent\n")

if __name__ == "__main__":

  root = tkinter.Tk()
  root.title("Lab-Monitor Server")
  root.geometry("1024x768")
  root.resizable(False, False)

  title = tkinter.Label(root, text="Lab-Monitor Server", font=("Serif", 32))
  title.pack()

  serverBtn = tkinter.Button(root, text="Start Server", command=serverBtnCommand)
  serverBtn.pack()

  logArea = tkinter.Text(root, height=40, width=130, bg="#E6E6E6")
  logArea.pack()

  Thread(target=server, args=(SERVER_PORT, logArea)).start()
  root.mainloop()
