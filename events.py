import logger
import psutil
import time
import os
import socket
import subprocess

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def USBEvents(serverSocket):

  oldDevices = psutil.disk_partitions()
  logger.log("Listening to partition mount events", serverSocket)

  while True:

    newDevices = psutil.disk_partitions()

    if(len(newDevices) > len(oldDevices)):
      logger.log("New Partition Mounted", serverSocket)

    elif(len(newDevices) < len(oldDevices)):
      logger.log("Partition Unmounted", serverSocket)

    oldDevices = newDevices
    time.sleep(0.5)

def networkEvents(serverSocket):

  logger.log("Listening to network events", serverSocket)
  ip = get_ip()

  env = dict(os.environ)  # make a copy of the environment
  lp_key = 'LD_LIBRARY_PATH'  # for Linux and *BSD.
  lp_orig = env.get(lp_key + '_ORIG')

  if lp_orig is not None:
      env[lp_key] = lp_orig  # restore the original, unmodified value
  else:
    # This happens when LD_LIBRARY_PATH was not set.
    # Remove the env var as a last resort:
    env.pop(lp_key, None)

  dumpFilter = f"ip and host {ip} and port not 53 and port not 138 and port not 5353 and ((tcp[tcpflags] & tcp-syn != 0) and not udp)"
  dumpProcess = subprocess.Popen(("tcpdump", "-l", "-nn", dumpFilter), stdout=subprocess.PIPE, env=env)

  for row in iter(dumpProcess.stdout.readline, b''):

    log = row.decode("utf8")
    tokenisedLog = log.split()

    src = tokenisedLog[2]
    dest = tokenisedLog[4].rstrip(":")

    try:
      srcService = socket.getservbyport(int(src.split(".")[-1]))
      src = f"{srcService.upper()} {'.'.join(src.split('.')[0:-1])}" 
    except:
      split = src.split(".")
      src = ".".join(split[0:-1]) + ":" + split[-1]
    
    try:
      destService = socket.getservbyport(int(dest.split(".")[-1]))
      dest = f"{destService.upper()} {'.'.join(dest.split('.')[0:-1])}" 
    except:
      split = src.split(".")
      src = ".".join(split[0:-1]) + ":" + split[-1]
      
    logger.log(f"{src} --> {dest}", serverSocket)
