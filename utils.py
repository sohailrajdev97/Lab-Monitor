import simplecrypt

def decrypt(messageBytes):

  f = open("./key", "r")
  key = f.read()
  f.close()

  try:
    message = simplecrypt.decrypt(key, messageBytes).decode("utf8")

  except:
    return "NA"

  return message


def getServerPort(message):

  # Return the server port if messageBytes is a server-init message. Else returns -1
 
  if len(message.split("@")) == 2 and message.split("@")[0] == "server-init" :

    try:
      return int(message.split("@")[1])
    
    except:
      return -1

  else:
    return -1