#!/usr/bin/python

import sys
import socket 
import Aikisado
import threading

port = 2306
maxClients = 100

seekList = []#"one", "two", "three", "four"]
seekListLock = threading.Lock()

#Function that deals with the client 
def handleClient( clientSock, address ):
	#TODO#Implement Locking
	try :
		#Check for correct client version 
		string = clientSock.recv(1024)
		clientVersion = string[4:].split('.')
		if (clientVersion < version):
			#Client is wrong version!
			print "old client!"
			clientSock.send("ver="+version[0]+"."+version[1]+"."+version[2])
		else :
			clientSock.send("welcome "+ address[0])
			if (clientVersion > version):
				print "\tThere may be a newer version!"
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
					#removing the name from the list if necessary to prevent duplicates
					num = seekList.index(address[0])
					seekList.pop(num) #removes the address
					seekList.pop(num-1) #removes the name component
				except :
					pass

				name = string[5:]
				if (name != "") :
					#print "appending ", string[5:], to the seek list"
					##seekListLock.acquire()
					seekList.append(string[5:])
					seekList.append(address[0])
					##seekListLock.release()
					
				#print seekList
			
			elif (string[:6] == "cancel"):
				try :
					#Removing the name from the list as requested
					num = seekList.index(address[0])
					seekList.pop(num) #removes the address
					seekList.pop(num-1) #removes the name component
				except :
					pass
			
			else :
				print "received bad string!"
				string = "kill"
		except :
			string = "kill"

	if (name != ""):
		#Disconnecting from client; remove from list.
		try:
			num = seekList.index(address[0])
			seekList.pop(num) #removes the address
			seekList.pop(num-1) #removes the name component
		except:
			pass
	print "thread dead!"

def serviceLoop(servSock):
	while 1 :
		try:
			print "Waiting for next client..."
			(clientSock, address) = servSock.accept()
			print "Client Connected, Creating Thread"
			threading.Thread(target=handleClient, args=(clientSock, address)).start()
		except:
			print "Exiting Service."
			servSock.close()
			break	
	
#Main Program
def start(background=False): 
	global version
	version = Aikisado.version
	print "Starting Server ("+version+")"
	version = version.split(".")
	servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	servSock.bind(('', port))
	servSock.listen(maxClients)
	if not background:
		serviceLoop(servSock)
	else:
		print "Background feature not yet working!"
		serviceLoop(servSock)
		#service = threading.Thread(target=serviceLoop,args=(servSock,))
		#service.daemon = True #Daemons die with the main process, this should not be used.
		#service.start()
	
if __name__ == "__main__":
	start()