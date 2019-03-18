def pollEvents(pollObject):
  while True:
    for fd, event in pollObject.poll():
      yield fd, event