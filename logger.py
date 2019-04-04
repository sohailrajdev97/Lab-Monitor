import os
import re
import uuid
from datetime import datetime

def formatMessage(message):
  macAddress = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
  return f"Machine MAC: {macAddress} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} {message} \n"

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

  try:
    serverSocket.sendall((formatMessage(message) + "~").encode("utf8"))

  except Exception as e:
    file.write(formatMessage("Could not send to the server. Maybe the server socket is closed"))
  
  file.close()
