from cryptography.fernet import Fernet

def decrypt(messageBytes):

  file = open("./key", "r")
  key = file.read().encode("utf8")
  file.close()

  try:
    f = Fernet(key)
    message = f.decrypt(messageBytes)

  except:
    return "NA"

  return message.decode("utf8")


def getServerPort(message):

  # Return the server port if messageBytes is a server-init message. Else returns -1
 
  if len(message.split("@")) == 2 and message.split("@")[0] == "server-init" :

    try:
      return int(message.split("@")[1])
    
    except:
      return -1

  else:
    return -1