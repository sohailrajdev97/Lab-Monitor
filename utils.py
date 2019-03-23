def getServerPort(messageBytes):

  # Return the server port if messageBytes is a server-init message. Else returns -1

  message = messageBytes.decode("ascii")
  
  if len(message.split("@")) == 2 and message.split("@")[0] == "server-init" :

    try:
      return int(message.split("@")[1])
    
    except:
      return -1

  else:
    return -1