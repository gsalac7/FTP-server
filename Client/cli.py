import commands
import socket
import sys
import time

###################################################
# Create the ephemeral port, and create the initial 
# socket to the port
###################################################
def get_ephemeral_port():
	welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	welcomeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	welcomeSocket.bind(('', 0))

	port_num = welcomeSocket.getsockname()[1]
	welcomeSocket.close()
	return port_num

#############################################################
# This function will be used to send data using the protocol
# we have set up, using the first 10 bytes as the length,
# and then the message. The data can be anythn from commands,
# to results of the ls system call.
# This is NOT going to be used for sending and receiving
# files, this will be sent through the initial TCP Connection
# with the port number specified by the user
# params: connSocket, the connection socket of the TCP connection
# params: the data
#############################################################
def send_data(connSocket, data):
	# Get the size of the data read
	# and convert it to string
	dataSizeStr = str(len(data))
	
	# Prepend 0's to the size string
	# until the size is 10 bytes
	while len(dataSizeStr) < 10:
		dataSizeStr = "0" + dataSizeStr
	# Prepend the size of the data to the
	data = dataSizeStr + data
	# The number of bytes sent
	numSent = 0
	
	# Send the data!
	while len(data) > numSent:
		numSent += connSocket.send(data[numSent:])

################################################################
# This function will be used to receive the data expecting our
# appropriate protocol.
# This receive function will NOT be used to send or receive files
#################################################################
def receive_data(connSocket):
	data_size_buffer = recvAll(connSocket, 10)
	data_size = int(data_size_buffer)
	data = recvAll(connSocket, data_size)
	return data

############################################
# This function will actually send the file 
# to the server using the same protocol
# params - file_name: the name of the file
# the user wants to transfer
############################################
def send_file(file_name, port_num):
	# Server address
	serverAddr = ''

	# ephemeral Server port
	serverPort = int(port_num)

	# The name of the file
	fileName = file_name

	# Open the file
	fileObj = open(fileName, "r")

	# Create a TCP socket
	connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect to the server
	connSock.connect((serverAddr, serverPort))

	# The number of bytes sent
	numSent = 0

	# The file data
	fileData = None

	# Keep sending until all is sent
	while True:
		# Read all the bytes of data
		fileData = fileObj.read()
		
		# Make sure we did not hit EOF
		if fileData:
			# Get the size of the data read
			# and convert it to string
			dataSizeStr = str(len(fileData))
			
			# Prepend 0's to the size string
			# until the size is 10 bytes
			while len(dataSizeStr) < 10:
				dataSizeStr = "0" + dataSizeStr
		
			# Prepend the size of the data to the
			# file data.
			fileData = dataSizeStr + fileData	
			
			# The number of bytes sent
			numSent = 0
			
			# Send the data!
			while len(fileData) > numSent:
				numSent += connSock.send(fileData[numSent:])
		else:
			break
		
	print "Sent ", numSent, " bytes."
		
	# Close the socket and the file
	connSock.close()
	fileObj.close()

##########################################
# Receive the data from the sender
##########################################
def recvAll(sock, numBytes):
	# The buffer
	recvBuff = ""
	
	# The temporary buffer
	tmpBuff = ""
	
	# Keep receiving till all is received
	while len(recvBuff) < numBytes:
		
		# Attempt to receive bytes
		tmpBuff = sock.recv(numBytes)
		
		# The other side has closed the socket
		if not tmpBuff:
			break
		
		# Add the received bytes to the buffer
		recvBuff += tmpBuff

	return recvBuff

################################################
# Function to download the data from the sender
################################################
def download_data(file_name, port_num):
	# The port on which to listen
	listenPort = port_num

	# Create a welcome socket. 
	welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Bind the socket to the port
	welcomeSock.bind(('', listenPort))

	# Start listening on the socket
	welcomeSock.listen(1)

	# Accept connections forever
	while True:
		
		print "Waiting for connections..."
			
		# Accept connections
		clientSock, addr = welcomeSock.accept()
		
		print "Accepted connection from client: ", addr
		print "\n"
		
		# The buffer to all data received from the
		# the client.
		fileData = ""
		
		# The temporary buffer to store the received
		# data.
		recvBuff = ""
		
		# The size of the incoming file
		fileSize = 0	
		
		# The buffer containing the file size
		fileSizeBuff = ""
		
		# Receive the first 10 bytes indicating the
		# size of the file
		fileSizeBuff = recvAll(clientSock, 10)
		# Get the file size
		fileSize = int(fileSizeBuff)
	
		print "The file size is ", fileSize
		
		# Get the file data
		fileData = recvAll(clientSock, fileSize)
		
		print 'File Received'

		# rewrite the file data in a new file
		file_obj = open(file_name, 'w')
		file_obj.write(fileData)
		file_obj.close()
			
		# Close our side
		clientSock.close()
		# break from the loop
		break

################################################
# Set up the initial TCP connection
################################################
def main():
	if len(sys.argv) < 2:
		print "USAGE python " + sys.argv[0] + " <PORT NUMBER>" 
		exit(1)

	# This is the server address
	serverAddr = ''
	# this is the port number for the intial TCP connection
	serverPort = int(sys.argv[1])

	# Create a TCP socket
	connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	connSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# Connect to the server using a different port
	connSock.connect((serverAddr, serverPort))

	command = ''
	while command != 'quit':
		command = raw_input('FTP > ')
		if command == 'ls':
			send_data(connSock, command) # send the ls call to the server
			results = receive_data(connSock) # receive the contents ls call to the server
			print results
		elif command == 'lls':
			# print the contents of the client
			value = ''
			for line in commands.getoutput('ls -l'):
				value += line
			print str(value)
		elif command.startswith('put'):
			send_data(connSock, command) # send the command
			file_name = command.split(' ')[1] 
			port_num = get_ephemeral_port() # create the ephemeral port
			send_data(connSock, str(port_num)) # send the ephemeral port number to use
			print 'Uploading the file...'
			time.sleep(1)
			send_file(file_name, port_num) # send the file using the ephemeral port
		elif command.startswith('get'):
			send_data(connSock, command)
			port_num = receive_data(connSock) # receive the port number
			file_name = command.split(' ')[1]
			download_data(file_name, int(port_num)) # get ready to download a file from the server
		elif command == 'quit':
			send_data(connSock, command) # tell the server we are quitting
	connSock.close()

if __name__ == '__main__':
	main()