# Assignment 3 FTP Server

## By: Gabe Salac

### Description:
- This program implements a simple FTP server written in Python 2.7

- The user will specify the port number to start the initial TCP connection to the server. This connection will be used to send commands to the server. This way the server will know whether the client will download a file, upload a file, send its contents, or quit the connection. Since FTP is an out of band protocol, when sending the file, the sender will generate an ephemeral port and use that port for the transmisison of the files

- The application protocol will use the first ten bytes to store the length of the data. This way the receiver will know how much data is being sent by the sender. The sender will also read the amount of bytes the file has, store that length in the message, and send to the receiver. The receiver will know to stop receiving based on the length of the first 10 bytes.

- When sending the file from either the client or the server, the sender will send the ephemeral port number to the receiver through the initial TCP connection. When sending the data, it will go through the ephemeral port.

### To Execute:
```
python serv.py <port number>
```
```
python cli.py <port number>
```
### How to use:
To upload a file:
```
FTP > put <filename>
```

To download a file from the server:
```
FTP > get <filename>
```
To list segments in the client directory:
```
FTP > lls
```
To list segments in the server directory:
```
FTP > ls
```
