import argparse
import socket
import select
from threading import Thread, Event
import tkinter
from simplecrypt import encrypt

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

def server(serverPort, logArea, terminateFlag):
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

  while not terminateFlag.is_set():
    for fd, event in pollObject.poll(3000):
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
    Thread(target=sendInitMessage, args=(CLIENT_PORT, SERVER_PORT)).start()
  
  else:
    logArea.insert(tkinter.END, "Sending stop message ....\n")
    serverBtn["text"] = "Start Server"
    Thread(target=sendStoptMessage, args=(CLIENT_PORT, )).start()

def terminate():
  terminateFlag.set()
  root.destroy()

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Lab-Monitor Server')
  parser.add_argument("-c", "--client", help="Client Port", type=int, default=45001)
  parser.add_argument("-s", "--server", help="Server Port", type=int, default=45000)
  args = parser.parse_args()

  SERVER_PORT = args.server
  CLIENT_PORT = args.client

  root = tkinter.Tk()
  root.title("Lab-Monitor Server")
  root.geometry("1024x768")
  root.resizable(False, False)

  title = tkinter.Label(root, text="Lab-Monitor Server", font=("Serif", 32))
  title.pack()

  portLabel = tkinter.Label(root, text=f"Server Port: {SERVER_PORT}  Client Port: {CLIENT_PORT}")
  portLabel.pack()

  serverBtn = tkinter.Button(root, text="Start Server", command=serverBtnCommand)
  serverBtn.pack()

  logArea = tkinter.Text(root, height=40, width=130, bg="#E6E6E6")
  logArea.pack()

  terminateFlag = Event()
  Thread(target=server, args=(SERVER_PORT, logArea, terminateFlag)).start()

  root.protocol("WM_DELETE_WINDOW", terminate)
  root.mainloop()
