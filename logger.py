import os

def formatMessage(message):
  return message + "\n"

def flushLogs():

  try:
    # Try to remove already existing log file
    os.remove("./logs.txt")  
  except:
    # File does not exist
    pass

def log(message, serverSocket):

  file = open("./logs.txt", "a+")
  file.write(formatMessage(message))

  if serverSocket.getSocket() is None:
    file.write(formatMessage("Not connected to a server. Logs will be written to the disk."))

  else:
    serverSocket.getSocket().sendall((formatMessage(message) + "~").encode("ascii"))
  
  file.close()
