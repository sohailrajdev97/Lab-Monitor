class MutableSocket:

  def __init__(self):
    self.socket = None
  
  def getSocket(self):
    return self.socket
  
  def setSocket(self, socket):
    self.socket = socket
    