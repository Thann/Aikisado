#!/usr/bin/python

import sys, socket, threading

version = "0.3.0"
port = 2306
maxClients = 100

seekList = []#"one", "two", "three", "four"]
seekListLock = threading.Lock()

#Function that deals with the client 
def handleClient( clientSock, address ):
	
	try :
		#Check for correct client version 
		string = clientSock.recv(1024)
		if (not string == "ver="+version):
			#Client is wrong version!
			clentSock.send("ver=" + version)
		else :
			clientSock.send("welcome "+ address[0])
	except :
		string = "kill"	
		
	name = ""
	#string = "init"
	while (string != "kill"):
		try:
			string = clientSock.recv(1024)
			print "received: ", string
			
			if (string == "gimme da list bro!"):
				#print "sending list.."
				for item in seekList :
					#print "sending: ", item
					clientSock.send(item)
					string = clientSock.recv(1024)
					#print string
				#print "done sending"
				clientSock.send("Done")

			elif (string[:4] == "name"):
				try :
					#removing the name from the list if nessicary to prevent duplicates
					num = seekList.index(address[0])
					seekList.pop(num) #removes the address
					seekList.pop(num-1) #removes the name component
				except :
					pass

				#print "appending ", string[5:], to the seek list"
				name = string[5:]
				##seekListLock.aquire()
				seekList.append(string[5:])
				seekList.append(address[0])
				##seekListLock.release()
				#print seekList
			
			else :
				print "recieved bad string!"
				string = "kill"
		except :
			string = "kill"

	if (name != ""):
		num = seekList.index(address[0])
		seekList.pop(num) #removes the address
		seekList.pop(num-1) #removes the name component
	print "thread dead!"

#Main Program
print "Starting Server"
servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servSock.bind(('', port))
servSock.listen(maxClients)		
while 1 :
	print "Waiting for next client..."
	(clientSock, address) = servSock.accept()
	print "Client Connected, Creating Thread"
	threading.Thread(target=handleClient, args=(clientSock, address)).start()
