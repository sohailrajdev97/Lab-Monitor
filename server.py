import argparse
import socket
import select
from threading import Thread, Event
import tkinter
from cryptography.fernet import Fernet

# Read the AES key
file = open("./key", "r")
key = file.read().encode("utf8")
file.close()

terminateFlag = Event()

def sendInitMessage(clientPort, serverPort):
  f = Fernet(key)
  INIT_MESSAGE = f"server-init@{serverPort}".encode("utf8")
  broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  broadcastSocket.sendto(f.encrypt(INIT_MESSAGE), ('<broadcast>', clientPort))
  broadcastSocket.close()

def sendStoptMessage(clientPort):
  f = Fernet(key)
  STOP_MESSAGE = "server-stop".encode("utf8")
  broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  broadcastSocket.sendto(f.encrypt(STOP_MESSAGE), ('<broadcast>', clientPort))
  broadcastSocket.close()

def logMessage(msg, logArea, logFile):
  logArea.insert(tkinter.END, msg)
  logArea.yview(tkinter.END)
  logFile.write(msg)

def server(serverPort, logArea, terminateFlag):
  # Create a socket for accepting incoming TCP connections from clients
  serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  serverSocket.bind(('', serverPort))
  serverSocket.listen()

  # Define data structures for async IO
  clientSockets = { serverSocket.fileno(): serverSocket }
  logFiles = { }
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
          logMessage(f"ABNORMAL DISCONNECTION: Client {address} with pending data: {pendingData}\n", logArea, logFiles[sock.fileno()])
          
        else:
          logMessage(f"Disconnection: Client {address}\n", logArea, logFiles[sock.fileno()])
        
        pollObject.unregister(fd)
        logFiles[sock.fileno()].close()
        del logFiles[sock.fileno()]
        del clientSockets[fd]
      
      elif sock is serverSocket:

        # New Connection
        sock, address = sock.accept()

        sock.setblocking(False)
        clientSockets[sock.fileno()] = sock
        addresses[sock] = address
        logFiles[sock.fileno()] = open(f"server_logs/{sock.getpeername()[0]}.txt", "w")
        pollObject.register(sock, select.POLLIN)

        logMessage(f"New Connection from {address}\n", logArea, logFiles[sock.fileno()])
      
      elif event & select.POLLIN:

        # Incoming data
        nextData = sock.recv(4096)

        if not nextData:
          sock.close()
          continue
        
        totalData = bytesReceived.pop(sock, b'') + nextData

        if(totalData.endswith(b'~')):
          logMessage(f"{addresses[sock][0]}: {totalData.decode('utf8')[:-1]}", logArea, logFiles[sock.fileno()])

        else:
          bytesReceived[sock] = totalData

  print("Server stopped")

def serverBtnCommand():

  if(serverBtn["text"] == "Start Server"):
    logArea.insert(tkinter.END, "Sending connection request ....\n")
    serverBtn["text"] = "Stop Server"
    terminateFlag.clear()
    Thread(target=server, args=(SERVER_PORT, logArea, terminateFlag)).start()
    Thread(target=sendInitMessage, args=(CLIENT_PORT, SERVER_PORT)).start()
  
  else:
    logArea.insert(tkinter.END, "Sending stop message ....\n")
    serverBtn["text"] = "Start Server"
    terminateFlag.set()
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

  root.protocol("WM_DELETE_WINDOW", terminate)
  root.mainloop()
