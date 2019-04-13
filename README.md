# Lab Monitor

## Project Design

This project has been designed to run on Linux and macOS. The setup instructions are provided in the sections that follow. The
project is divided into two parts, the server and the client.

### Server

- The server is multi-threaded. The thread information is as follows:
  - One thread to display the GUI, display client logs and handle the user interactions
  - Separate threads to send start and stop messages to the client. These have to be sent in a separate thread to prevent the UI from freezing when the message is being sent
  - One thread to handle all the incoming messages from the clients. This thread receives the client requests in an asynchronous manner and thus, this is non-blocking
- The main data structures which the server maintains are:
  - `clientSockets` : A dictionary which stores the sockets of currently connected clients
  - `logFiles` : A dictionary which stores the handles of log files (one for each connected client)
  - `addresses` : A dictionary which stores the addresses of connected clients mapped to the file number of the corresponding socket
- Server by default runs on the port 45000. A custom port can be specified using the `-s` command line argument
- Server can only send the following messages to the clients through a UDP datagram
  - `server-init@PORT` : This message is used to notify clients to start the monitoring process. PORT is the port number at which the server is listening for client’s response (defaults to 45000)
  - `server-stop` : This message is used to notify clients to stop the monitoring process

### Client

- The client is multi-process based. The main process manages the following child processes:
  - One process to listen to USB (or partition mount) events
  - One process to monitor the network activity
- Client runs on port 45001 by default. A custom port can be used by `-p` argument at the runtime
- The client has to be started with super user permissions so that the network activity can be monitored
- The packets are filtered according to the following criteria:
  - Packets with port 53 in header are ignored so that DNS requests are not reported
  - ARP packets are not reported. Only IP packets are reported
  - UDP packets are reported
  - TCP packets with SYN or ACK flag set are reported. This is done because we are only interested in reporting the event when the TCP session / transfer is initiated. Reporting each and every packet after the TCP session initiation will log a lot of packets and thus it will be difficult to monitor the log when a lot of clients are connected
 - For monitoring USB activity, long polling is used. The child process checks for any new partition mounts / unmounts after every 500 milliseconds. The polling method is inefficient as compared to using an interrupt when USB device is attached but it does have some advantages which outweigh its disadvantages:
  - If we use some utility such as udev to listen for USB events, the client won’t be cross platform as udev is only available for Linux systems. We require third party utilities for macOS and Windows in this case.
  - udev cannot detect the event when a partition is mounted over the network. If someone tries to mount a network partition, it will be detected by the polling technique but udev will not report any such incident.

## Process Workflow

1. Clients run on every system when the system boots.
1. Client listens on a fixed port (defaults to 45001)
1. Client listens for a message from the server
1. Server is started on a system specifying the port at which clients are listening on the remote systems
1. Server sends a server-init message as a UDP datagram to the broadcast interface of the network
1. All the clients receive and validate this message
1. If the message is valid, clients initiate a TCP connection by taking the server’s IP from the source of datagram and server’s port from server-init message
1. Client starts the child processes
1. All the logs are sent to the server in real-time
1. Server displays the logs in the GUI and also stores the logs in a file (a separate file for each client it is connected to)
1. After the evaluation, server-stop is sent by the server to the clients
1. After this message is received by the clients, the child processes and monitoring is stopped.
1. Client again waits for a new server-init message

## Security Measures

- Server and client share an encryption key
- The messages which are sent by the server on broadcast interface are symmetrically encrypted
- Client tries to decrypts the datagram. If a valid message is detected, client performs the required operation. Otherwise, the message is discarded.

## System Requirements

Requirements for building the project from source code:

- Python 3.6+
- pip for installing dependencies
- Python cryptography module for encryption
- Python psutil module for detecting partition mount/unmount events
- Linux / macOS based system

## Setup Instructions

- Download / clone the project from Github
- Execute `pip install -r requirements.txt` on terminal to install the dependencies. You may have to use pip3 instead of pip depending on your default python installation
- Generate a new key using `python3 keygen.py`. The newly generated key is written to a key file in the project directory. This should be kept safely, and if leaked, may result in a security breach. Note that a default key is provided with the project but it is highly recommended to generate a new one
- Run the client using `sudo python3 client.py`. A custom port can be specified using `-p` option. Such as `sudo python3 client.py -p 12345`
- Run the server using `python3 server.py`. A custom port can be specified using the `-s` argument for the server and `-c` for the client. For example with, `python3 server.py -s 12345 -c 4444` server will start at port 12345 and will connect to the clients running at port 4444
- Click the Start Server button. Logs will be displayed on-screen and written as files to the directory server_logs/ . Logs in the files can only be accessed after the server is stopped
- After the evaluation, click Stop Server button
