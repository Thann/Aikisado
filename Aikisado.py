#!/usr/bin/python

import sys
try:  
	import pygtk  
	pygtk.require("2.0")  
except:  
	pass  
try:  
	import gtk  
except:  
	print("GTK Not Availible")
	sys.exit(1)


class GameBoard:

	global version 
	global port
	global serverAddress
	global tileSize
	
	#Initialized as if in "init"...
	version = "0.2.1"
	port = 2306
	serverAddress = "192.168.1.155"
	tileSize = 48
	

	#Starts with the the bottom right corner
	boardLayout = ["Orange", "Blue", "Purple", "Pink", "Yellow", "Red", "Green", "Brown",
			"Red", "Orange", "Pink", "Green", "Blue", "Yellow", "Brown", "Purple",
			"Green", "Pink", "Orange", "Red", "Purple", "Brown", "Yellow", "Blue",
			"Pink", "Purple", "Blue", "Orange", "Brown", "Green", "Red", "Yellow",
			"Yellow", "Red", "Green", "Brown", "Orange", "Blue", "Purple", "Pink",
			"Blue", "Yellow", "Brown", "Purple", "Red", "Orange", "Pink", "Green",
			"Purple", "Brown", "Yellow", "Blue", "Green", "Pink", "Orange", "Red",
			"Brown", "Green", "Red", "Yellow", "Pink", "Purple", "Blue", "Orange"]

	#These are at the bottom
	blackPieceLayout = ["Orange", "Blue", "Purple", "Pink", "Yellow", "Red", "Green", "Brown",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",	
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL"]

	whitePieceLayout = ["NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"Brown", "Green", "Red", "Yellow", "Pink", "Purple", "Blue", "Orange"]
	
	sumoPieceLayout = ["NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",
				"NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL",]


	
	def __init__( self , table, status ):
		#Stores a local list of the eventBoxs (tiles)
		#The tiles at the bottom right corner are first
		self.table = table.get_children()
		#Keeps track of the statusLabel
		self.status = status
		#initalize Lists; [0:64] makes it a copy instead of a reference.
		self.eligible = self.blackPieceLayout[0:64]
		self.currentBlackLayout = self.blackPieceLayout[0:64]
		self.currentWhiteLayout = self.whitePieceLayout[0:64]
		self.currentSumoLayout = self.sumoPieceLayout[0:64]
		self.showMoves = "True"
		self.turn = "White"
		self.blackWins = 0
		self.whiteWins = 0

	def reset( self ):
		self.firstTurn = "True"
		self.winner = "False"
		self.selectedPiece = -1
		self.eligible = self.blackPieceLayout[0:64]
		#Swap turn so the looser goes first this time
		if (self.turn == "Black"):
			self.turn = "White"
		else :
			self.turn = "Black"
		self.status.set_text("Player Turn: "+self.turn)

		#Sets all of the images to have the name of their index and blanks the board
		for index, item in enumerate(self.table):			
			item.get_child().set_name(str(index))
			self.removePiece(index)
			
		#Place the Black pieces
		for index, item in enumerate(self.currentBlackLayout):	
			if (item != "NULL"):
				self.placePiece( index, item, "Black" )

		#Place the White pieces
		for index, item in enumerate(self.currentWhiteLayout):	
			if (item != "NULL"):
				self.placePiece( index, item, "White" )
				
			
	#Takes an Int marking the position of the tile clicked on
	def selectSquare( self, num ):
		#Determines what the user should be selecting
		if (self.firstTurn == "True"):	
			#The user is selecting or re-selecting one of his/her pieces this only happens on the first turn
			if (self.selectedPiece >= 0):
				#Remove The Selection Mark from the previously selected piece; the user is re-selecting
				self.removePiece(self.selectedPiece)
				self.placePiece( self.selectedPiece, self.boardLayout[self.selectedPiece], self.turn )
			#Verify there is a valid piece on the selected square
			if (self.turn == "Black" and self.currentBlackLayout[num] != "NULL" and self.currentWhiteLayout[num] == "NULL"):
				#The Black Player has selected a Black Piece
				self.selectedPieceColor = self.currentBlackLayout[num]
				self.selectedPiece = num
				self.markSelected()
				self.determineMoves()
				#return True
			elif (self.turn == "White" and self.currentWhiteLayout[num] != "NULL" and self.currentBlackLayout[num] == "NULL"):
				#The White Player has selected a White Piece
				self.selectedPieceColor = self.currentWhiteLayout[num]
				self.selectedPiece = num
				self.markSelected()
				self.determineMoves()
				#return True
			elif (self.selectedPiece >= 0): 			
				#The user has clicked on a blank square after selecting a piece
				if (self.eligible[num] == "GOOD"):
					self.firstTurn = "False"
					self.makeMove( num )
					return True
				else :
					#needed to keep the selected piece highlighted when the user clicks on an invalid square
					self.markSelected() 
			#Else, there is no initial piece selected and therefore nothing happens
		else :
			#The User is  selecting a destination 
			if (self.eligible[num] == "GOOD"):
				ret = self.makeMove( num )
				return ret
			#Else, the user selected a non-blank square and nothing will happen
			
		return False
			
	#Move the selectedPiece to num, choose the new selected piece, mark it, and swap turns
	def makeMove( self, num ):	
		ret = True
		possibleBonus = 0		
		if (self.turn == "Black") and (self.currentWhiteLayout[num] != "NULL"):
			#Black Sumo Push!
			self.removePiece( self.selectedPiece )
			self.removePiece( num )
			if (self.currentWhiteLayout[num+8] != "NULL"):
				#Double Push - take all of the below procedures one step further
				self.removePiece(num+8)
				self.currentSumoLayout[num+16] = self.currentSumoLayout[num+8]
				self.placePiece(num+16, self.currentWhiteLayout[num+8], "White")
				self.currentWhiteLayout[num+16] = self.currentWhiteLayout[num+8]
				possibleBonus = 8 #Makes sure that the location of the second pushed piece determines the color of the next move 
			#Modify current sumo Layout
			self.currentSumoLayout[num-8] = self.currentSumoLayout[num]
			self.currentSumoLayout[num] = self.currentSumoLayout[self.selectedPiece]
			self.currentSumoLayout[self.selectedPiece] = "NULL"		
			self.placePiece( num, self.selectedPieceColor, "Black" )
			self.placePiece( num+8, self.currentWhiteLayout[num], "White" )
			#Modify Selected Piece Layout, No need to switch turns
			self.currentBlackLayout[self.selectedPiece] = "NULL"
			self.currentBlackLayout[num] = self.selectedPieceColor
			self.currentWhiteLayout[num+8] = self.currentWhiteLayout[num]
			self.currentWhiteLayout[num] = "NULL"	
			#select the BLACK piece that is the color of the tile the WHITE piece was just pushed onto
			self.selectedPiece = self.currentBlackLayout.index(self.boardLayout[num+8+possibleBonus])
			self.selectedPieceColor = self.boardLayout[num+8+possibleBonus]
			self.status.set_text("Sumo Push -> Player Turn: Black")
		elif (self.turn == "White") and (self.currentBlackLayout[num] != "NULL"):
			#White Sumo Push!
			self.removePiece( self.selectedPiece )
			self.removePiece( num )
			if (self.currentBlackLayout[num-8] != "NULL"):
				#Double Push
				self.removePiece(num-8)
				self.currentSumoLayout[num-16] = self.currentSumoLayout[num-8]
				self.placePiece(num-16, self.currentBlackLayout[num-8], "Black")
				self.currentBlackLayout[num-16] = self.currentBlackLayout[num-8]
				possibleBonus = 8
			#Modify current sumo Layout
			self.currentSumoLayout[num-8] = self.currentSumoLayout[num]
			self.currentSumoLayout[num] = self.currentSumoLayout[self.selectedPiece]
			self.currentSumoLayout[self.selectedPiece] = "NULL"
			#self.currentSumoLayout[num] = "NULL"
			self.placePiece( num, self.selectedPieceColor, "White" )
			self.placePiece( num-8, self.currentBlackLayout[num], "Black" )
			#Modify Selected Piece Layout, No need to switch turns
			self.currentWhiteLayout[self.selectedPiece] = "NULL"
			self.currentWhiteLayout[num] = self.selectedPieceColor
			self.currentBlackLayout[num-8] = self.currentBlackLayout[num]
			self.currentBlackLayout[num] = "NULL"
			#select the WHITE piece that is the color of the tile the BLACK piece was just pushed onto
			self.selectedPiece = self.currentWhiteLayout.index(self.boardLayout[num-8-possibleBonus])
			self.selectedPieceColor = self.boardLayout[num-8-possibleBonus]
			self.status.set_text("Sumo Push -> Player Turn: White")
		else : 
			#Regular Move
			self.removePiece( self.selectedPiece )
			#Move the sumo qualifier for regular moves (not pushes)
			if (self.currentSumoLayout[self.selectedPiece] != "NULL"):
				self.currentSumoLayout[num] = self.currentSumoLayout[self.selectedPiece]
				self.currentSumoLayout[self.selectedPiece] = "NULL"
			self.placePiece( num, self.selectedPieceColor, self.turn )	
			
			#Modify the selected piece layout and switch turns
			if (self.turn == "Black"):
				self.currentBlackLayout[self.selectedPiece] = "NULL"
				self.currentBlackLayout[num] = self.selectedPieceColor
				self.turn = "White"
				#find the next turns selected piece by searching the piece List for its color 
				self.selectedPiece = self.currentWhiteLayout.index(self.boardLayout[num])
			else :
				self.currentWhiteLayout[self.selectedPiece] = "NULL"
				self.currentWhiteLayout[num] = self.selectedPieceColor
				self.turn = "Black"
				#find the next turns selected piece by searching the appropriate piece List for its color 
				self.selectedPiece = self.currentBlackLayout.index(self.boardLayout[num])
			#Match the selectedPieceColor to the selectedPiece
			self.selectedPieceColor = self.boardLayout[num]
			self.status.set_text("Player Turn: "+self.turn)

		#If Someone Won... num is the position if the piece that won.
		#possitions 0-7 and 56-63 are the home rows. if any piece moves into a home row, someone won
		if (num <= 7) or (num >= 56):
			points = 1
			#undo turn swap and add points
			if (self.turn == "Black"):
				if (self.currentSumoLayout[num] == "SuperWhite"):
					points = 3
				elif (self.currentSumoLayout[num] == "White"):
					points = 2

				self.turn = "White"
				self.whiteWins = self.whiteWins+points
			else :
				if (self.currentSumoLayout[num] == "SuperBlack"):
					points = 3
				elif (self.currentSumoLayout[num] == "Black"):
					points = 2

				self.turn = "Black"
				self.blackWins = self.blackWins+points

			#Sumo and SuperSumo promote the piece that won
			if (self.currentSumoLayout[num] != "NULL"):
				self.currentSumoLayout[num] = "Super"+self.turn
			else :
				self.currentSumoLayout[num] = self.turn

			self.status.set_text(self.turn + " Wins!")
			self.winner = "True"
			
			#Temp Layouts are holding the piece positions from the end of this round for sumo logic
			tempBlackLayout = self.currentBlackLayout[0:64]
			tempWhiteLayout = self.currentWhiteLayout[0:64]
	
			##Reformat the PieceLayouts
			#Current Layouts are how the pieces will be arranged at the start of the next game.
			self.currentBlackLayout = self.blackPieceLayout[0:64]#Placeholder for actual logic.
			self.currentWhiteLayout = self.whitePieceLayout[0:64]#Placeholder for actual logic.
			
			#reformat sumo list to move all of the sumos to their home row
			tempSumoLayout = self.currentSumoLayout[0:64]
			self.currentSumoLayout = self.sumoPieceLayout[0:64]
			for index, item in enumerate(tempSumoLayout):
				if (item == "Black") or (item == "SuperBlack"):
					#Qualify the new piece in the position based on the color of the piece in the old layout
						#and the index of that piece in the new layout
					#tempBlackLayout[index] is the color of the piece
					#self.currentBlackLayout.index() finds the index of a specific color
					self.currentSumoLayout[self.currentBlackLayout.index(tempBlackLayout[index])] = item
				elif (item == "White") or (item == "SuperWhite"): 
					self.currentSumoLayout[self.currentWhiteLayout.index(tempWhiteLayout[index])] = item

			#clear the possible moves
			for index, item in enumerate(self.eligible):
				if (item == "GOOD"):
					self.removePiece(index)
					if (self.turn == "Black") and (self.currentWhiteLayout[index] != "NULL"):
						#There was a Sumo Push available when toggled
						self.placePiece( index, self.currentWhiteLayout[index], "White" )
					elif (self.turn == "White") and (self.currentBlackLayout[index] != "NULL"):
						self.placePiece( index, self.currentBlackLayout[index], "Black" )

						
		else:
			#determine the possible moves for next turn
			self.determineMoves()
			while not ("GOOD" in self.eligible):
				#if there are no moves: skip the players turn
				ret = False
				self.selectedPieceColor = self.boardLayout[self.selectedPiece]
				if (self.turn == "Black"):
					self.turn = "White"
					self.selectedPiece = self.currentWhiteLayout.index(self.boardLayout[self.selectedPiece])
					self.status.set_text("Skipping Black -> Player Turn: White")
				else :
					self.turn = "Black"
					self.selectedPiece = self.currentBlackLayout.index(self.boardLayout[self.selectedPiece])
					self.status.set_text("Skipping White -> Player Turn: Black")
				self.determineMoves()

			self.markSelected()
		return ret
				
	#Place Piece over existing BG
	def placePiece( self, num, color, player ):
		#GET BG PIXBUFF
		bg = self.table[num].get_child().get_pixbuf()
		#Get Piece PIXBUFF		
		piece = gtk.gdk.pixbuf_new_from_file("GUI/" + color + player + "Piece.png")
		if (self.currentSumoLayout[num] != "NULL"):
			#Get Sumo PIXBUFF and Composite it onto the Piece
			sumo = gtk.gdk.pixbuf_new_from_file("GUI/Sumo"+self.currentSumoLayout[num]+".png")
			sumo.composite(piece, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
		#Composite Piece Over BG
		piece.composite(bg, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
		#Set the tile to contain the new image
		self.table[num].get_child().set_from_pixbuf(bg)

	#Place Eligible Mark over existing Piece/BG
	def markEligible( self, num ):
		#GET BG PIXBUFF
		bg = self.table[num].get_child().get_pixbuf()
		#Get Mark PIXBUFF	
		if (self.currentBlackLayout[num] != "NULL"):
			mark = gtk.gdk.pixbuf_new_from_file("GUI/SumoPushDown.png")
		elif (self.currentWhiteLayout[num] != "NULL"):
			mark = gtk.gdk.pixbuf_new_from_file("GUI/SumoPushUp.png")
		else :
			mark = gtk.gdk.pixbuf_new_from_file("GUI/EligibleMark.png") 
		#Composite Mark Over BG
		mark.composite(bg, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
		#Set the tile to contain the new image
		self.table[num].get_child().set_from_pixbuf(bg)
				
	#Set the BG to the layout default (solid color)
	def removePiece( self, num ):
		#Restores the tile to its original solid BG color
		self.table[num].get_child().set_from_file("GUI/" + self.boardLayout[num] + "BG.jpg")
	
	
	#Place Brackets over existing Piece/BG 
	def markSelected( self ):
		#GET BG PIXBUFF
		bg = self.table[self.selectedPiece].get_child().get_pixbuf()
		#Get Mark PIXBUFF		
		mark = gtk.gdk.pixbuf_new_from_file("GUI/SelectedMark.png") 
		#Composite Mark Over BG
		mark.composite(bg, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
		#Set the tile to contain the new image
		self.table[self.selectedPiece].get_child().set_from_pixbuf(bg)

	#fills up eligible[] and places marks.
	def determineMoves( self ):
		num = self.selectedPiece
		#go through and unmark everything
		if (self.showMoves == "True"):
			for index, item in enumerate(self.eligible):
				#oldNum is used to prevent blanking the piece that just moved
				if (item == "GOOD"): # and (index != oldNum):
					self.removePiece(index)
					#check to see if you removed a piece
					if (self.currentBlackLayout[index] != "NULL"):
						#This (index) is where the previously selected piece moved too
						#or a Sumo was eligible to push but didn't; remove marker.
						self.placePiece(index, self.currentBlackLayout[index], "Black")
					elif (self.currentWhiteLayout[index] != "NULL"):
						self.placePiece(index, self.currentWhiteLayout[index], "White")
		
		#Re-determining what is eligible
		self.eligible = self.currentBlackLayout[0:64]
		for index, item in enumerate(self.currentWhiteLayout):	
			if (item != "NULL"):
				self.eligible[index] = item

		self.eligible[num] = "GOOD"
		
		#Unprofessionally determines which positions are valid.
		if (self.turn == "Black"):
			#looks for viable moves above num
			i = 0
			#this algorithm relies on the fact that every 7th space from the origin is on the diagonal, etc.
			#num%8 is the position along the row(0-7). it can iterate this may times before it hits a wall
			#7-num/8 is the number of times it can iterate before hitting the ceiling
			while (i < num%8) and (i < 7-num/8) and (self.eligible[i*7+num] == "GOOD"): 	
				i = i + 1
				#checks every 7th to make sure its not occupied.
				if (self.eligible[i*7+num] == "NULL"):
					if (self.currentSumoLayout[num] == "NULL") or ((self.currentSumoLayout[num] == "Black") and (i <= 5)) or ((self.currentSumoLayout[num] == "SuperBlack") and (i <= 3)):
						#not a sumo or is but within distance limit
						self.eligible[i*7+num] = "GOOD"	

			i = 0
			while (i < 7-num/8) and (self.eligible[i*8+num] == "GOOD"):			
				i = i + 1				
				if (self.eligible[i*8+num] == "NULL"):
					if (self.currentSumoLayout[num] == "NULL") or ((self.currentSumoLayout[num] == "Black") and (i <= 5)) or ((self.currentSumoLayout[num] == "SuperBlack") and (i <= 3)):
						self.eligible[i*8+num] = "GOOD"

			i = 0
			while (i < 7-num%8) and (i < 7-num/8) and (self.eligible[i*9+num] == "GOOD"):
				i = i + 1		
				if (self.eligible[i*9+num] == "NULL"):
					if (self.currentSumoLayout[num] == "NULL") or ((self.currentSumoLayout[num] == "Black") and (i <= 5)) or ((self.currentSumoLayout[num] == "SuperBlack") and (i <= 3)):
						self.eligible[i*9+num] = "GOOD"
			
			#looks for a Sumo Push - if the selected piece is a sumo and has a non sumo enemy piece directly in front with space to push. 
			#(will overwrite good if there is no piece directly in front)
			if (self.currentSumoLayout[num] != "NULL") and (num <= 47):
				#Single Sumo Push
				if (self.currentWhiteLayout[num+8] != "NULL") and ((self.currentSumoLayout[num+8] == "NULL") or (self.currentSumoLayout[num] == "SuperBlack")) and (self.eligible[num+16] == "NULL"):
					self.eligible[num+8] = "GOOD"

			elif (self.currentSumoLayout[num] == "SuperBlack") and (num <= 39):
				#Double Sumo Push
				if (self.currentWhiteLayout[num+8] != "NULL") and (self.currentWhiteLayout[num+16] != "NULL") and (self.currentSumoLayout[num+8] != "SuperWhite") and (self.currentSumoLayout[num+16] != "SuperWhite") and (self.eligible[num+24] == "NULL"):
					self.eligible[num+8] = "GOOD"
				
		else :
			#looks for viable moves below num
			i = 0
			#7-num%8 is the position along the row(0-7). it can iterate this may times before it hits a wall
			#num/8 is the number of times it can iterate before hitting the floor
			while (i < 7-num%8) and (i < num/8) and (self.eligible[num-i*7] == "GOOD"): 	
				i = i + 1
				if (self.eligible[num-i*7] == "NULL"):
					if (self.currentSumoLayout[num] == "NULL") or ((self.currentSumoLayout[num] == "White") and (i <= 5)) or ((self.currentSumoLayout[num] == "SuperWhite") and (i <= 3)):
						self.eligible[num-i*7] = "GOOD"	

			i = 0
			while (i < num/8) and (self.eligible[num-i*8] == "GOOD"):			
				i = i + 1				
				if (self.eligible[num-i*8] == "NULL"):
					if (self.currentSumoLayout[num] == "NULL") or ((self.currentSumoLayout[num] == "White") and (i <= 5)) or ((self.currentSumoLayout[num] == "SuperWhite") and (i <= 3)):
						self.eligible[num-i*8] = "GOOD"

			i = 0
			while (i < num%8) and (i < num/8) and (self.eligible[num-i*9] == "GOOD"):	
				i = i + 1		
				if (self.eligible[num-i*9] == "NULL"):
					if (self.currentSumoLayout[num] == "NULL") or ((self.currentSumoLayout[num] == "White") and (i <= 5)) or ((self.currentSumoLayout[num] == "SuperWhite") and (i <= 3)):
						self.eligible[num-i*9] = "GOOD"

			#looks for a Sumo Push
			if (self.currentSumoLayout[num] != "NULL") and (num >= 16):
				#Single Sumo Push
				if (self.currentBlackLayout[num-8] != "NULL") and ((self.currentSumoLayout[num-8] == "NULL") or (self.currentSumoLayout[num] == "SuperWhite")) and (self.eligible[num-16] == "NULL"):
					self.eligible[num-8] = "GOOD"
			
				elif (self.currentSumoLayout[num] == "SuperWhite") and (num >= 24):
					#Double Sumo Push
					if (self.currentBlackLayout[num-8] != "NULL") and (self.currentBlackLayout[num-16] != "NULL") and (self.currentSumoLayout[num-8] != "SuperBlack") and (self.currentSumoLayout[num-16] != "SuperBlack") and (self.eligible[num-24] == "NULL"):
						self.eligible[num-8] = "GOOD"
		
		#so that the selected piece is not marked.
		self.eligible[num] = "BAD"

		if (self.showMoves == "True"):
			#go through and mark everything 
			for index, item in enumerate(self.eligible):
				if (item == "GOOD"):
					self.markEligible(index) 
	
	def ShowMoves( self, movesOn ):
		if (self.showMoves == "False") and (movesOn):
			#Display the possible moves!
			self.showMoves = "True"
			for index, item in enumerate(self.eligible):
				if (item == "GOOD"):
					self.markEligible(index)

		elif ((self.showMoves == "True") and not (movesOn)):
			#Remove the possible moves marks from the board 
			self.showMoves = "False"
			for index, item in enumerate(self.eligible):
				if (item == "GOOD"):
					self.removePiece(index)
					if (self.turn == "Black") and (self.currentWhiteLayout[index] != "NULL"):
						#There was a Sumo Push available when toggled
						self.placePiece( index, self.currentWhiteLayout[index], "White" )
					elif (self.turn == "White") and (self.currentBlackLayout[index] != "NULL"):
						self.placePiece( index, self.currentBlackLayout[index], "Black" )
						
		#Else nothing really changed.
		
#end of class: GameBoard

			
class NetworkConnection():
		
	import socket, threading, time

	#the state of this "connection" is held by self.connectionStatus. possible values include:
	#Server - connected to the lobby server and browsing opponents
	#awaiting response - a challenge has been issued
	#awaiting challenge - the seek loop is running
	#challenge received - the user has been challenged 
	#game 
	#dead

	def __init__( self, cbw ):
		print "Trying to contact game server at ", serverAddress  
		self.callBackWidget = cbw
		self.connectionStatus = "Bad"
		self.callBack = False ##find more elegant method
		global seekStatus
		seekStatus = "Kill"
		self.lobbySock = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
		self.lobbySock.settimeout(3)
		try : 
			self.lobbySock.connect((serverAddress , port))
			self.connectionStatus = "Server"
			string = self.lobbySock.recv(1024)
			self.localIP = string[8:]
			#print "ip = "+ string[8:]
		
		except :
			print "Server not found"			

	def getList( self ):
	#try :
		self.lobbySock.send("gimme da list bro!")
		seekList = []
		while (True):
			#print "more data coming"
			string = self.lobbySock.recv(1024)
			if (string == "Done"):
				#print "Done Recieveing"
				break
			#print "appending: ", string
			seekList.append(string)
			self.lobbySock.send("OK")
	#except :
		#print "list retrieve failed"
		#seekList = ["Please Refresh",""]

		return seekList
	
	def seekOpponent(self, name):
		global seekStatus
		try:
			if (seekStatus != "Running"):
				#set client's name
				self.name = name
				self.lobbySock.send("name="+name)
				print "threading seek process..."
				seekStatus = "Running"
				self.challengeLock = self.threading.Lock()
				##self.challengeLock.aquire()
				self.threading.Thread(target=self.seekLoop, args=()).start()
			else :
				print "already seeking"
		except:
			print "oops! seek init failed..."

	def seekLoop(self):
		#waiting for remote user to issue challenge
		global seekStatus
		self.servSock = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
		self.servSock.bind(('', port+1))
		self.servSock.listen(1)
		self.servSock.settimeout(5)
		print "Waiting for Opponent..."
		while (seekStatus != "Kill"):
			try :
				self.connectionStatus = "awaiting challenge"
				(self.gameSock, self.address) = self.servSock.accept()
				print "challenged!!"
				#return Signal
				self.connectionStatus = "challenge received"
				self.callBack = True
				self.callBackWidget.activate()
				##self.challengeLock.aquire()
				#self.time.sleep(5)
				break
			except:
				line = "wasted" #there needs to be something here so this fills the space
				#print "accept timed out"
		print "seek ended..."
		seekStatus = "Kill"

	def stopSeek(self):
		print "canceling seek"
		global seekStatus
		seekStatus = "Kill"

	def challenge(self, ip):
		#issue challenge and wait for the potential oppoent to respond to your challenge
		if (seekStatus == "Running"):
			self.stopSeek()
		print "issued challenge to ip: ", ip
		self.threading.Thread(target=self.challengeThread, args=(ip, "stub")).start()

	def challengeThread(self, ip, stub):
		##try :
		self.gameSock = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
		self.gameSock.settimeout(15)
		self.gameSock.connect((ip , port+1))
		string = self.gameSock.recv(1024)
		print "re: ", string
		if (string == "challenge accepted"):
			self.connectionStatus = "challenge accepted"
			print "challenge accepted!"
		else :
			print "challenge rejected."
		
		#except :
		#print "challenge ignored."
		print "yo!"
		self.callBack = True
		self.callBackWidget.activate()
		
	def answerChallenge(self, accept, localColor):
		#reply to the remote user who challenged you
		if (accept):
			print "challenge accepted!"
			if (self.connectionStatus == "challenge received"):
				self.gameSock.send("challenge accepted")
			self.connectionStatus = "Game"
			self.disconect()
			self.gameSock.settimeout(5)
			if (localColor == "White"):
				self.threading.Thread(target=self.moveLoop, args=()).start()
			##self.challengeLock.release()
		else :
			#challenge declined... seek must be restarted
			print "challenge declined."
			self.gameSock.send("challenge declined")
			self.seekOpponent(self.name)
		
	def status( self ):
		return self.connectionStatus

	def disconect(self):
		self.stopSeek()
		try :
			self.lobbySock.close()
		except : 
			print "disconect failed."
			#self.gameSock.close()


	def moveLoop(self):
		#print "starting move loop..."
		while (True):
			try :
				string = self.gameSock.recv(1024)
				print "recieved: ", string
				if (string[0:4] == "Move"):
					self.recentMove = string[5:]
					self.callBack = True
					self.callBackWidget.activate()
				elif (string[0:4] == "Turn"):
					#print "Its the local players turn."
					break
				else : 
					print "something got messed up while waiting for the remote move..." ##deal with this more specifically
					break
			except : 
				line = "Wasted" #something needs to go here... ##pass?

		#print "move loop ended..."

	def getMove(self):
		return int(self.recentMove)
				
	def sendMove( self, pos, turnOver ):
		##try:
		##thread this to improve local speed
		print "Sending Move: ", pos
		self.gameSock.send("Move="+str(pos))
		if (turnOver):
			#let the remote player know its their turn
			self.time.sleep(1)
			self.gameSock.send("Turn!")
			#wait for response
			#moveLoopRunning = True
			self.threading.Thread(target=self.moveLoop, args=()).start() 

#end of class: 	NetworkConnection
	
	
class GameGui:

	import threading

	def __init__( self ):
		#loads the GUI file
		self.builder = gtk.Builder()
		self.builder.add_from_file("GUI/main.ui")
		self.activeWindow = "gameWindow"
		self.localColor = "Null"
		self.startNewGame()
		
		#format the tree View
		seekTreeView = self.builder.get_object("seekTreeView")
		cellRend = gtk.CellRendererText()
		nameColl = gtk.TreeViewColumn("Name", cellRend, text=0)
		ipColl = gtk.TreeViewColumn("IP", cellRend, text=1)
		seekTreeView.append_column(nameColl)
		seekTreeView.append_column(ipColl)
		self.seekStore = gtk.ListStore(str, str)
		seekTreeView.set_model(self.seekStore)
		seekTreeView.set_reorderable(True)

		#outlines each event and associates it with a local function
		dic = { 
			#Global Events
			"gtk_widget_hide" : self.widgetHide,
			
			#Main Window
	        	"on_gameWindow_destroy" : self.quit,
			"tile_press_event" : self.tilePressed,
			"on_gameWindow_focus_in_event" : self.maintainFocus,
			"on_callBack_activate" : self.callBack,

			#Toolbar
	        	"on_newGameToolButton_clicked" : self.newGameDialog,
	        	"on_undoToolButton_clicked" : self.stub,
			"on_zoomToolButton_toggled" : self.stub,
			"on_showMovesToolButton_toggled" : self.toggleMoves,
			"on_helpToolButton_clicked" : self.help,
			"on_aboutToolButton_clicked" : self.about,

			#New Game Window
			"on_newGameOKButton_clicked" : self.startNewGame,
			"on_newGameCancelButton_clicked" : self.newGameDialogHide,

			#Lobby Window
			"on_lobbySeekButton_clicked" : self.seekNetworkGame,
			"on_lobbyRefreshButton_clicked" : self.lobbyRefresh,#self.callBack,
			"on_lobbyCancelButton_clicked" : self.lobbyCancel,
			"on_lobbyChallengeButton_clicked" : self.issueChallenge,
			
			#challenge Window
			"on_yesChallengeButton_clicked" : self.startNetworkGame,
			"on_noChallengeButton_clicked" : self.declineChallenge,
			
			#Grats Window
			"on_gratsOkButton_clicked" : self.gratsHide,
			
		}
		self.builder.connect_signals( dic )
		

	def stub(self, widget):
		print "Feature not yet implemented."

	#For intercepting the "delete-event" and instead closing
	def widgetHide(self, widget, trigeringEvent):
		self.activeWindow = "gameWindow"
		widget.hide()
		return True

	def quit(self, widget):
		sys.exit(0)

	def tilePressed(self, widget, trigeringEvent):
		#print "Pressed Button: ", widget.get_child().get_name()
		#pass the board the gameTable so it can mess with the images.
		if (self.board.winner != "True"): 
			if (self.gameType == "Local") or (self.board.turn == self.localColor):
				moveSuccess = self.board.selectSquare(int(widget.get_child().get_name()))
				#print "Move Success: "+str(moveSuccess)
				if (moveSuccess):
					self.builder.get_object("statusLabel").set_text("It's the Remote Players turn...")
				if (self.gameType == "Network"):
					self.connection.sendMove(int(widget.get_child().get_name()), moveSuccess)
						
			#Else: wait for remote player to select a piece	

		if (self.board.winner == "True"): 
			self.announceWinner()

	def announceWinner(self):
		if (self.gameType == "Network") and (self.board.turn != self.localColor):
			#the remote player won
			self.builder.get_object("gratsLabel").set_text("Sorry "+self.board.turn+",\n        You Lost..")
		else :
			#a local player won
			self.builder.get_object("gratsLabel").set_text("Congratulations "+self.board.turn+",\n        You Win!!")
		self.activeWindow ="gratsDialog"
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("gratsDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("gratsDialog").present()
		self.builder.get_object("scoreLabel").set_text("Black: "+str(self.board.blackWins)+" | White: "+str(self.board.whiteWins))
		

	def maintainFocus(self, widget, trigeringEvent):
		if (self.activeWindow != "gameWindow"):
			self.builder.get_object(self.activeWindow).present()
			#self.builder.get_object(self.activeWindow).grab_focus()

	def toggleMoves(self, widget):
		self.board.ShowMoves(self.builder.get_object("showMovesToolButton").get_active())
		
	def newGameDialog(self, widget):
		self.activeWindow = "newGameDialog"
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("newGameDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("newGameDialog").present()

	def newGameDialogHide(self, widget):
		self.activeWindow = "gameWindow"
		self.builder.get_object("newGameDialog").hide()
	
	def startNewGame(self, widget="stub"): 
		#connect to opponent
		if (self.builder.get_object("networkGameRadioButton").get_active()):
			self.connection = NetworkConnection(self.builder.get_object("lobbyRefreshButton"))#callBackWidget"))#challengeReceivedButton"))#lobbyRefreshButton"))) ##find better solution
			if (self.connection.status() == "Server"):
				print "Found Server!"
				#fill opponent list
				self.lobbyRefresh() #add items to list
				
				self.newGameDialogHide( self )
				self.activeWindow = "lobbyDialog"
				pos = self.builder.get_object("gameWindow").get_position()
				self.builder.get_object("lobbyDialog").move(pos[0]+25, pos[1]+75)
				self.builder.get_object("lobbyDialog").present()
			#Else, unable to reach server
	
		else :
			self.gameType = "Local"
			self.newGameDialogHide( self )
			self.board = GameBoard(self.builder.get_object("gameTable"), self.builder.get_object("statusLabel"))
			self.board.reset()
			self.builder.get_object("scoreLabel").set_text("Black: 0 | White: 0")


	def lobbyRefresh(self, widget="NULL"):
		#this button doubles as a call back for self.connection
		if (self.connection.callBack == True):
			self.connection.callBack = False
			self.callBack()
		else :
			seekList = self.connection.getList()
			self.seekStore.clear() #erases the list
			i = 0
			while (i < len(seekList)) :
				self.seekStore.append([seekList[i], seekList[i+1]])
				i = i +2
			if (len(seekList) == 0):
				#let the user know if there are no opponents
				self.seekStore.append(["", "Sorry, no opponents. Try seeking."])

	def lobbyCancel(self, widget):
		self.connection.disconect()
		self.activeWindow = "newGameDialog"
		self.builder.get_object("lobbyDialog").hide()
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("newGameDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("newGameDialog").present()

	def seekNetworkGame(self, widget):
		string = self.builder.get_object("hostName").get_text()
		if (string != ""):
			self.connection.seekOpponent(string)
			self.lobbyRefresh()

	def issueChallenge(self, widget):
		(model, iter) = self.builder.get_object("seekTreeView").get_selection().get_selected()
		name = self.seekStore.get_value(iter, 0)
		ip = self.seekStore.get_value(iter, 1)
		if (ip != self.connection.localIP): #makes sure your not trying to challenge yourself
			##show "please wait" popup
			self.connection.challenge(ip)

	def callBack(self, widget="Null"):
		if (self.connection.status() == "challenge received"):
			#challenge received from a remote player
			self.recieveChallenge()
		elif (self.connection.status() == "challenge accepted"):
			#the remote player accepted the locally issued challenge
			##close "please wait" popup
			self.localColor = "White" #this ensures that the player who is challenged goes first
			self.startNetworkGame()
		elif (self.connection.status() == "Game"):
			#moves a piece for the remote player
			moveSuccess = self.board.selectSquare(self.connection.getMove())
			if (moveSuccess): 
				self.builder.get_object("statusLabel").set_text("It's Your Turn!")
			if (self.board.winner == "True"): 
				self.announceWinner()		
			
	
	def recieveChallenge(self):
		print "Challenge Received!"
		self.localColor = "Black" #this ensures that the player who is challenged goes first
		opponentIP = self.connection.address[0]
		self.builder.get_object("challengeLabel").set_text("You have been challenged by a player at: "+ opponentIP +" !")
		self.activeWindow = "challengeDialog"
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("challengeDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("challengeDialog").present()

	def declineChallenge(self, widget):
		self.connection.answerChallenge(False, "Null")
		self.activeWindow = "lobbyDialog"
		self.builder.get_object("challengeDialog").hide()

	def startNetworkGame(self, widget="Null"): #called when a local/remote user accepts a challenge
		self.connection.answerChallenge(True, self.localColor)
		print "Your Color: "+self.localColor
		self.gameType = "Network"
		self.activeWindow = "gameWindow"
		self.builder.get_object("challengeDialog").hide()
		self.builder.get_object("lobbyDialog").hide()
		self.board = GameBoard(self.builder.get_object("gameTable"), self.builder.get_object("statusLabel"))
		self.board.reset()
		self.builder.get_object("scoreLabel").set_text("Black: 0 | White: 0")
		if (self.board.turn == self.localColor):
			self.builder.get_object("statusLabel").set_text("It's Your Turn!")
		else :
			self.builder.get_object("statusLabel").set_text("It's the Remote Players turn...")

	def help(self, widget):
		#self.activeWindow = "helpDialog"
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("helpDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("helpDialog").present()

	def about(self, widget):
		global version
		self.builder.get_object("aboutDialog").set_version(version)
		self.activeWindow = "aboutDialog"
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("aboutDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("aboutDialog").present()

	def gratsHide(self, widget):
		self.activeWindow = "gameWindow"
		self.builder.get_object("gratsDialog").hide()
		self.board.reset()
		if (self.board.turn == self.localColor):
			self.builder.get_object("statusLabel").set_text("It's Your Turn!")
		else :
			self.builder.get_object("statusLabel").set_text("It's the Remote Players turn...")
		

#end of class: GameGUI
		
gtk.gdk.threads_init() #Makes threads work
gui = GameGui()
gtk.main()
