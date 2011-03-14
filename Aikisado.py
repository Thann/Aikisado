#!/usr/bin/python

# Aikisado is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Aikisado is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with Aikisado. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import platform
import threading
import time
import gobject

try:
	import pygtk
	pygtk.require("2.0")
except:
	print "Missing Pygtk"
		
try:
	import gtk
except:
	print("GTK Not Available")
	sys.exit(1)


version = "0.3.2"
serverPort = 2306
gamePort = 2307 #forward this port on your router
serverAddress = "thanntastic.com"
tileSize = 48
updatesEnabled = True
pwd = os.path.abspath(os.path.dirname(__file__)) #location of Aikisado.py

class GameBoard:
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
	
	def __init__( self, table, status, enableAnimations, AIMethod = "NULL" ):
		#Stores a local list of the eventBoxs (tiles)
		#The tiles at the bottom right corner are first
		self.table = table.get_children()
		#Keeps track of the statusLabel
		self.status = status
		self.enableAnimations = enableAnimations
		self.AIMethod = AIMethod
		self.animationLock = threading.Lock()
		self.moves = []
		#initialize Lists; [:] makes it a copy instead of a reference.
		self.eligible = self.blackPieceLayout[:]#[0:64]
		self.currentBlackLayout = self.blackPieceLayout[:]
		self.currentWhiteLayout = self.whitePieceLayout[:]
		self.currentSumoLayout = self.sumoPieceLayout[:]
		self.showMoves = True
		self.sumoPush = False
		self.turn = "White"
		self.blackWins = 0
		self.whiteWins = 0
		
	def reset( self , mode = "Normal" ):
		self.killAnimation = True
		self.animationLock.acquire()
		self.animationLock.release()
		self.firstTurn = True
		self.winner = False
		self.selectedPiece = -1
		self.eligible = self.blackPieceLayout[:]
		self.moves.append("Reset: "+mode)
		
		#Temp Layouts are holding the piece positions from the end of this round for sumo logic
		tempBlackLayout = self.currentBlackLayout[:]
		tempWhiteLayout = self.currentWhiteLayout[:]
			
		#Reformat the PieceLayouts
		if (mode == "RTL"): #Right To Left
			#Current Layouts are how the pieces will be arranged at the start of the next game.
			self.currentBlackLayout = self.sumoPieceLayout[:]#Blank
			self.currentWhiteLayout = self.sumoPieceLayout[:]#Blank
			#Place the Black pieces
			tempIndex = 0
			currentIndex = 0
			while (currentIndex <= 7): #Only Tries to place first 8 pieces
				if (tempBlackLayout[tempIndex] != "NULL"):
					self.currentBlackLayout[currentIndex] = tempBlackLayout[tempIndex]
					currentIndex = currentIndex + 1
				tempIndex = tempIndex + 1
			#Place the White pieces
			tempIndex = 63
			currentIndex = 63
			while (currentIndex >= 56):
				if (tempWhiteLayout[tempIndex] != "NULL"):
					self.currentWhiteLayout[currentIndex] = tempWhiteLayout[tempIndex]
					currentIndex = currentIndex - 1
				tempIndex = tempIndex - 1
		elif (mode == "LTR"): #Left To Right
			self.currentBlackLayout = self.sumoPieceLayout[:]#Blank
			self.currentWhiteLayout = self.sumoPieceLayout[:]#Blank
			#Place the Black pieces
			tempIndex = 7
			currentIndex = 7
			while (currentIndex >= 0): #Only Tries to place first 8 pieces
				if (tempBlackLayout[tempIndex] != "NULL"):
					self.currentBlackLayout[currentIndex] = tempBlackLayout[tempIndex]
					currentIndex = currentIndex - 1
				if (tempIndex % 8 == 0): #temp goes like this: 7,6,5,4,3,2,1,0,15,14,13,12,11,10,9,8,23,22...
					tempIndex = tempIndex + 15
				else :
					tempIndex = tempIndex - 1
					
			#Place the White pieces
			tempIndex = 56
			currentIndex = 56
			while (currentIndex <= 63):
				if (tempWhiteLayout[tempIndex] != "NULL"):
					self.currentWhiteLayout[currentIndex] = tempWhiteLayout[tempIndex]
					currentIndex = currentIndex + 1
				if (tempIndex % 8 == 7): 
					tempIndex = tempIndex - 15
				else :
					tempIndex = tempIndex + 1
		else : #Pieces go on their matching color
			self.currentBlackLayout = self.blackPieceLayout[:]
			self.currentWhiteLayout = self.whitePieceLayout[:]
		
		#reformat sumo list to move all of the sumos to their home row
		tempSumoLayout = self.currentSumoLayout[:]
		self.currentSumoLayout = self.sumoPieceLayout[:]
		for index, item in enumerate(tempSumoLayout):
			if (item == "Black") or (item == "SuperBlack"):
				#Qualify the new piece in the position based on the color of the piece in the old layout
					#and the index of that piece in the new layout
				#tempBlackLayout[index] is the color of the piece
				#self.currentBlackLayout.index() finds the index of a specific color
				self.currentSumoLayout[self.currentBlackLayout.index(tempBlackLayout[index])] = item
			elif (item == "White") or (item == "SuperWhite"): 
				self.currentSumoLayout[self.currentWhiteLayout.index(tempWhiteLayout[index])] = item
				
		#save inital state for self.undo
		self.previousSelectedPiece = self.selectedPiece
		self.previousBlackLayout = self.currentBlackLayout[:]
		self.previousWhiteLayout = self.currentWhiteLayout[:]
		self.previousSumoLayout = self.currentSumoLayout[:]
					
		#Swap turn so the looser goes first this time
		if (self.turn == "White") or (not self.AIMethod == "NULL"):
			self.turn = "Black" #Player always goes first vs AI
		else :
			self.turn = "White" 

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
		if (self.firstTurn == True):	
			#The user is selecting or re-selecting one of his/her pieces this only happens on the first turn
			if (self.selectedPiece >= 0):
				#Remove The Selection Mark from the previously selected piece; the user is re-selecting
				self.removePiece(self.selectedPiece)
				if (self.turn == "Black"):
					self.placePiece( self.selectedPiece, self.currentBlackLayout[self.selectedPiece], self.turn )
				else:
					self.placePiece( self.selectedPiece, self.currentWhiteLayout[self.selectedPiece], self.turn )
			#Verify there is a valid piece on the selected square
			if (self.turn == "Black" and self.currentBlackLayout[num] != "NULL" and self.currentWhiteLayout[num] == "NULL"):
				#The Black Player has selected a Black Piece
				self.selectedPieceColor = self.currentBlackLayout[num]
				self.selectedPiece = num
				self.markSelected()
				#Aikisolver.determineMoves(self)
				self.determineMoves()
				#return True
			elif (self.turn == "White" and self.currentWhiteLayout[num] != "NULL" and self.currentBlackLayout[num] == "NULL"):
				#The White Player has selected a White Piece
				self.selectedPieceColor = self.currentWhiteLayout[num]
				self.selectedPiece = num
				self.markSelected()
				#Aikisolver.determineMoves(self)
				self.determineMoves()
				#return True
			elif (self.selectedPiece >= 0): 			
				#The user has clicked on a blank square after selecting a piece
				if (self.eligible[num] == "GOOD"):
					self.firstTurn = False
					self.makeMove( num )
					if (not self.AIMethod == "NULL"):
						self.makeMove(self.AIMethod(self))
					return True
				else :
					#needed to keep the selected piece highlighted when the user clicks on an invalid square
					self.markSelected() 
			#Else, there is no initial piece selected and therefore nothing happens
		else :
			#The User is selecting a destination (not firstTurn)
			if (self.eligible[num] == "GOOD"):
				self.previousSelectedPiece = self.selectedPiece
				self.previousBlackLayout = self.currentBlackLayout[:]
				self.previousWhiteLayout = self.currentWhiteLayout[:]
				self.previousSumoLayout = self.currentSumoLayout[:]
				ret = self.makeMove( num )
				if (ret and (not self.AIMethod == "NULL") and (not self.winner) and self.turn == "White"): #turn = black after sumo push.
					self.makeMove(self.AIMethod(self))

				return ret
			#Else, the user selected a non-blank square and nothing will happen
			
		return False
			
	#Move the selectedPiece to num, choose the new selected piece, mark it, and swap turns
	def makeMove( self, num ):	
		ret = True
		possibleBonus = 0		
		if (self.turn == "Black") and (self.currentWhiteLayout[num] != "NULL"):
			#TODO#Provide animation support
			#Black Sumo Push!
			self.sumoPush = True
			self.killAnimation = True
			self.recordMove("Push", self.selectedPiece, num)
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
			self.currentSumoLayout[num+8] = self.currentSumoLayout[num]
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
			self.sumoPush = True
			self.killAnimation = True
			self.recordMove("Push", self.selectedPiece, num)
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
			self.recordMove("Move", self.selectedPiece, num)
			#Move the sumo qualifier for regular moves (not pushes)
			if (self.currentSumoLayout[self.selectedPiece] != "NULL"):
				self.currentSumoLayout[num] = self.currentSumoLayout[self.selectedPiece]
				self.currentSumoLayout[self.selectedPiece] = "NULL"
	
			self.movePiece( self.selectedPiece, num, self.selectedPieceColor, self.turn )	
			
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
		#positions 0-7 and 56-63 are the home rows. if any piece moves into a home row, someone won
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
			self.winner = True

			#clear the possible moves
			#Duplicated at toggeleShowMoves()
			self.eligible[num] = "NULL"
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
			#Aikisolver.determineMoves(self)
			i = 0
			skipped = False
			while not ("GOOD" in self.eligible):
				skipped = True
				#If there are no moves: skip the players turn. Repeat if still no moves.
				i = i + 1
				if (ret == True):
					ret = False
				else :
					ret = True
				self.selectedPieceColor = self.boardLayout[self.selectedPiece]
				if (self.turn == "Black"):
					self.turn = "White"
					self.selectedPiece = self.currentWhiteLayout.index(self.boardLayout[self.selectedPiece])
					self.status.set_text("Skipping Black -> Player Turn: White")
					#print "Skipping Black -> Player Turn: White"
				else :
					self.turn = "Black"
					self.selectedPiece = self.currentBlackLayout.index(self.boardLayout[self.selectedPiece])
					self.status.set_text("Skipping White -> Player Turn: Black")
					#print "Skipping White -> Player Turn: Black"
				if (i == 9): #assumes that after 9 null moves there is a gridlock.
					#print "GridLock! Player who last moved loses. ("+self.turn+")"
					self.status.set_text("GridLock! Player who last moved loses. ("+self.turn+")")
					self.winner = True
					if (self.turn == "White"):
						self.turn = "Black"
						self.blackWins = self.blackWins + 1
					else :
						self.turn = "White"
						self.whiteWins = self.whiteWins + 1
					return ret
				#Aikisolver.determineMoves(self)
				self.determineMoves()
			#end while (no moves)
			#TODO# these are too hacky, there is probably another place to fix these issues
			if ((not self.AIMethod == "NULL") and self.turn == "White" and skipped):
				self.makeMove(self.AIMethod(self))
			if ((not self.AIMethod == "NULL") and self.turn == "White" and self.sumoPush):
				self.makeMove(self.AIMethod(self)) #make the AI move after is pushes
			if (self.sumoPush) or (not self.enableAnimations):
				self.markSelected()
		#end else (no winner)
		self.sumoPush = False
		return ret #returns true if the move is valid

	#Place Piece over existing BG
	def placePiece( self, num, pieceColor, playerColor ):
		#GET BG PIXBUFF
		bg = self.table[num].get_child().get_pixbuf()
		#Get Piece PIXBUFF		
		piece = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/"+pieceColor+playerColor+"Piece.png")
		if (self.currentSumoLayout[num] != "NULL"):
			#Get Sumo PIXBUFF and Composite it onto the Piece
			sumo = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/Sumo"+self.currentSumoLayout[num] + ".png")
			sumo.composite(piece, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
		#Composite Piece Over BG
		piece.composite(bg, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
		#Set the tile to contain the new image
		self.table[num].get_child().set_from_pixbuf(bg)

	#Starts the Animation for the movement of a game piece if enabled
	def movePiece( self, startingPosition, finalPosition, pieceColor, playerColor ):
		if (self.enableAnimations):
			#Prepare for the board for animations - (eligible changes the instant the thread starts)
			#go through and unmark everything
			if (self.showMoves):
				for index, item in enumerate(self.eligible):
					if (item == "GOOD"):
						self.removePiece(index)
						#check to see if you removed a piece
						if (self.currentBlackLayout[index] != "NULL"):
							#This (index) is where the previously selected piece moved to
							#or a Sumo was eligible to push but didn't; remove marker.
							self.placePiece(index, self.currentBlackLayout[index], "Black")
						elif (self.currentWhiteLayout[index] != "NULL"):
							self.placePiece(index, self.currentWhiteLayout[index], "White")

			#Start animationThread()
			self.killAnimation = False
			threading.Thread(target=self.animationThread, args=(startingPosition, finalPosition, pieceColor, playerColor)).start()
		else :
			self.removePiece( self.selectedPiece )
			self.placePiece( finalPosition, self.selectedPieceColor, self.turn )
		
	#Animates a piece over the backGround then returns the the board to its normal state
	def animationThread( self, startingPosition, finalPosition, pieceColor, playerColor ):
		#Wait for an already running animation to finish
		self.animationLock.acquire()
		
		#Declare animation constants
		timeToCrossOneSquare = 0.08 #0.1875 Will cross the board in 1.5 seconds
		framesPerSquare = 8 #Number of times the image should be refreshed when crossing one square
		pixPerFrame = tileSize / framesPerSquare #should divide cleanly (% = 0)
		
		#Calculate Width, Height, topLeftCorner, displacements, & startingPixel
		xDisplacement = finalPosition%8 - startingPosition%8 #Positive when traveling North (^) 
		yDisplacement = finalPosition/8 - startingPosition/8 #Positive when traveling West (<-)
		if (yDisplacement < 0): #White Move
			height = yDisplacement * -1
			if (xDisplacement < 0): # \
				width = xDisplacement * -1
				topLeftCorner = startingPosition
				startingPixel = (0, 0)
			else : # /
				width = xDisplacement
				topLeftCorner = startingPosition+width
				startingPixel = ((width)*tileSize, 0)
		else : #Black Move
			height = yDisplacement
			if (xDisplacement < 0): # /
				width = xDisplacement * -1
				topLeftCorner = finalPosition+width
				startingPixel = (0, (height)*tileSize)
			else : # \
				width = xDisplacement
				topLeftCorner = finalPosition
				startingPixel = ((width)*tileSize, (height)*tileSize)
				
		width = width + 1
		height = height + 1
		hijackedSquares = []
		
		#Create a master backGround pixbuf of the affected areas
		backGround = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width*tileSize, height*tileSize)
		for h in range(height):
			for w in range(width):
				pos = topLeftCorner-(w)-(h*8)
				hijackedSquares.append(pos)
				#print "pos: ",pos," - (",w,", ",h,")"
				tmpPixbuf = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/" + self.boardLayout[pos] + "BG.jpg")
				tmpPixbuf.composite(backGround, w*tileSize, h*tileSize, tileSize, tileSize, w*tileSize, h*tileSize, 1, 1, gtk.gdk.INTERP_HYPER, 255)
				#set the squares to subPixbuffs of the backGround - when the background pixbif gets updates so does its subpixbufs
				self.table[pos].get_child().set_from_pixbuf(backGround.subpixbuf(w*tileSize, h*tileSize, tileSize, tileSize))
				
		#Add the static pieces to the backGround
		tabooColor = self.boardLayout[finalPosition] #This is needed only for AI games where the next move may appear during animation becasue both moves modify the board before the animation occurs.
		for index, item in enumerate(hijackedSquares):
			if (self.currentBlackLayout[item] != "NULL") and (item != finalPosition):
				self.placePiece( item, self.currentBlackLayout[item], "Black" )
			elif (self.currentWhiteLayout[item] != "NULL") and (item != finalPosition) and (self.currentWhiteLayout[item] != tabooColor):
				self.placePiece( item, self.currentWhiteLayout[item], "White" )
		
		#Calc Animation variables
		numberOfFrames = framesPerSquare*(height-1)
		frameWaitTime = timeToCrossOneSquare / framesPerSquare #1/FPS
		blankBackGround = backGround.copy()

		#Convert the displacements to the direction of travel from the starting pixel 
		if (xDisplacement >= 1):
			xDisplacement = -1
		elif (xDisplacement <= -1): 
			xDisplacement = 1
		#Else xDisplacement should stay the same
		if (yDisplacement >= 1):
			yDisplacement = -1
		elif (yDisplacement <= -1): 
			yDisplacement = 1
		
		#Repeatedly move piece on the master backGround and refresh the widgets
		for i in range(numberOfFrames):
			if (self.killAnimation):
				break
			blankBackGround.composite(backGround, 0, 0, width*tileSize, height*tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
			piece = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/"+pieceColor+playerColor+"Piece.png")
			#print "pos: (",(i*xDisplacement*pixPerFrame)+startingPixel[0],", ",(i*yDisplacement*pixPerFrame)+startingPixel[1],")"
			#(i*xDisplacement*pixPerFrame)+tileSize = the X-position to place the piece 
			piece.composite(backGround, (i*xDisplacement*pixPerFrame)+startingPixel[0], (i*yDisplacement*pixPerFrame)+startingPixel[1], tileSize, tileSize, (i*xDisplacement*pixPerFrame)+startingPixel[0], (i*yDisplacement*pixPerFrame)+startingPixel[1], 1, 1, gtk.gdk.INTERP_HYPER, 255)
			self.table[0].get_parent().queue_draw()
			time.sleep(frameWaitTime)
		
		#Replace the static pieces
		for index, item in enumerate(hijackedSquares):
			self.removePiece(item)
			if (self.currentBlackLayout[item] != "NULL"):
				self.placePiece( item, self.currentBlackLayout[item], "Black" )
			elif (self.currentWhiteLayout[item] != "NULL"):
				self.placePiece( item, self.currentWhiteLayout[item], "White" )
		
		self.placePiece(finalPosition, pieceColor, playerColor)
		if not (self.winner):
			self.markSelected() #if the selected piece was in the animated area.
			self.markEligible()
		self.animationLock.release()
		
	#Place Eligible Mark over existing Piece/BG
	def markEligible( self ):
		if (self.showMoves):
			for index, item in enumerate(self.eligible):
				if (item == "GOOD"):
					self.placeMarker(index)

	
	def placeMarker(self, num):
		#GET BG PIXBUFF
		bg = self.table[num].get_child().get_pixbuf()
		#Get Mark PIXBUFF	
		if (self.currentBlackLayout[num] != "NULL"):
			mark = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/SumoPushDown.png")
		elif (self.currentWhiteLayout[num] != "NULL"):
			mark = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/SumoPushUp.png")
		else :
			mark = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/EligibleMark.png") 
		#Composite Mark Over BG
		mark.composite(bg, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
		#Set the tile to contain the new image
		self.table[num].get_child().set_from_pixbuf(bg)
				
	#Set the BG to the layout default (solid color)
	def removePiece( self, num ):
		#Restores the tile to its original solid BG color
		self.table[num].get_child().set_from_file(pwd+"/GUI/" + self.boardLayout[num] + "BG.jpg")
	
	#Place Brackets over existing Piece/BG 
	def markSelected( self ):
		#GET BG PIXBUFF
		bg = self.table[self.selectedPiece].get_child().get_pixbuf()
		#Get Mark PIXBUFF		
		mark = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/SelectedMark.png") 
		#Composite Mark Over BG
		mark.composite(bg, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
		#Set the tile to contain the new image
		self.table[self.selectedPiece].get_child().set_from_pixbuf(bg)

	#fills up eligible[] and places marks.
	def determineMoves( self ):
		num = self.selectedPiece
		#go through and unmark everything
		if (self.showMoves) and ((self.firstTurn) or (not self.enableAnimations) or (self.sumoPush)):
			for index, item in enumerate(self.eligible):
				if (item == "GOOD"): 
					self.removePiece(index)
					#check to see if you removed a piece
					if (self.currentBlackLayout[index] != "NULL"):
						#This (index) is where the previously selected piece moved to
						#or a Sumo was eligible to push but didn't; remove marker.
						self.placePiece(index, self.currentBlackLayout[index], "Black")
					elif (self.currentWhiteLayout[index] != "NULL"):
						self.placePiece(index, self.currentWhiteLayout[index], "White")
		
		self.eligible = Aikisolver.generateEligible(self)

		if ((self.firstTurn) or (not self.enableAnimations) or (self.sumoPush)):
			self.markEligible()

	def undo(self):
		#TODO#make work for Sumo Pushes
		self.selectedPiece = self.previousSelectedPiece
		if (self.turn == "Black") or (not self.AIMethod == "NULL"):
			self.currentWhiteLayout = self.previousWhiteLayout[:]
			self.selectedPieceColor = self.currentWhiteLayout[self.selectedPiece]
			self.moves.pop()
			if (self.AIMethod == "NULL"):
				tempTurn = "White"
		if (self.turn == "White") or (not self.AIMethod == "NULL"):
			self.currentBlackLayout = self.previousBlackLayout[:]
			self.selectedPieceColor = self.currentBlackLayout[self.selectedPiece]
			self.moves.pop()
			if (self.AIMethod == "NULL"):
				tempTurn = "Black"
		
		if (self.AIMethod == "NULL"):
			self.turn = tempTurn
		self.selectedPiece = self.previousSelectedPiece
		self.currentSumoLayout = self.previousSumoLayout[:]
		self.status.set_text("Player Turn: "+self.turn)
		self.eligible = Aikisolver.generateEligible(self)
		
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
		
		if (self.selectedPiece == -1):
			self.firstTurn = True
		else:
			self.markSelected()
			self.markEligible()

	def recordMove(self, moveType, fromSpace, toSpace):
		self.moves.append(moveType+self.turn+":"+str(fromSpace)+"("+self.boardLayout[fromSpace]+")"+" to:"+str(toSpace)+"("+self.boardLayout[toSpace]+")")
	
	def toggleShowMoves( self, movesOn ):
		if (not self.showMoves) and (movesOn):
			#Display the possible moves!
			self.showMoves = True
			self.markEligible()

		elif ((self.showMoves) and not (movesOn)):
			#Remove the possible moves marks from the board 
			self.showMoves = False
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

#library for determining moves
class Aikisolver():
	@staticmethod
	def tooEasyAI(gameBoard): 
		#just selects the farthest possible move
		assert(gameBoard.turn == "White") #Computer should always be black... for now at least
		eligible = Aikisolver.generateEligible(gameBoard)
		for index, item in enumerate(eligible):
			if item == "GOOD":
				return index
		return 0

	@staticmethod
	def easyAI(gameBoard):
		#Finds the farthest move that wont cause the human to win
		assert(gameBoard.turn == "White")
		#blackWins = whiteWins = []
		eligible = Aikisolver.generateEligible(gameBoard)
		humanWins = {}
		
		for index, item in enumerate(eligible): #look at every possible move
			if (item == "GOOD"):
				if (index <= 7):
					#found winning move
					return index
				
				color = gameBoard.boardLayout[index] #color of the board where were looking at
				if (not color in humanWins): #If the color has not yet been added to the human win-dict
					#Look for possible wins
					humanWins[color] = False
					tempEligible = Aikisolver.generateEligible(gameBoard, gameBoard.currentBlackLayout.index(color))
					for tempIndex, tempItem in enumerate(tempEligible): #for every possible move of the human piece
						if (tempItem == "GOOD" and tempIndex >= 56):
							humanWins[color] = True #the human will win if the AI lands on this color
							break
				
				if (not humanWins[color]):
					return index

		#There are no moves where he human player won't win, just select the farthest move.
		print "Human should Win.."
		for index, item in enumerate(eligible):
			if item == "GOOD":
				return index

		assert(False) #this should never be reached
	
	@staticmethod
	def mediumAI(gameBoard):
		#tries to threaten the home row and wont move to a place that will cause the opponenet to win
		#same as Medium but will prioritize skipping the humans turn
		assert(gameBoard.turn == "White")
		#blackWins = whiteWins = []
		eligible = Aikisolver.generateEligible(gameBoard)
		checkedColors = []
		
		if (not gameBoard.currentBlackLayout[gameBoard.selectedPiece-8] == "NULL") and (eligible[gameBoard.selectedPiece-8] == "GOOD"):
			#always do a sumo push if you can
			print "sumo push!"
			return gameBoard.selectedPiece-8
		
		for index, item in enumerate(eligible): #look at every possible move
			if (item == "GOOD"):
				if (index <= 7):
					#found winning move
					return index
				priority = 0
				color = gameBoard.boardLayout[index] #color of the board where were looking at
				if (not color in checkedColors): #If the color has not yet been added to the human win-dict
					#Look for possible human wins
					checkedColors.append(color)
					priority = 4 #will remain 4 if this piece has no moves and will cause the players turn to be skipped
					tempEligible = Aikisolver.generateEligible(gameBoard, gameBoard.currentBlackLayout.index(color))
					for tempIndex, tempItem in enumerate(tempEligible): #for every possible move of the human piece
						if (tempItem == "GOOD"):
							if (tempIndex >= 56):
								priority = 0 #the human will win if the AI lands on this color
								break
							priority = 1 #lowest feasible
				
				if (priority == 4):
					#TODO#makesure it will be worth it
					pass
				if (priority == 1):
					#Check for any moves that would threaten their home row
					tempEligible = Aikisolver.generateEligible(gameBoard, index)
					for tempIndex, tempItem in enumerate(tempEligible):
						if (tempItem == "GOOD" and tempIndex <= 7):	
							priority = 3 #threatens the home row
							break
				
				
				eligible[index] = "Priority="+str(priority)
							
		#find the best move
		move = (-1, -1)
		for index, item in enumerate(eligible):
			if (item[:4] == "Prio"):
				if (item[-1:] > move[0]):
					move = (item[-1:], index)

		#if (not move[0] == -1): #if move was set
		return move[1]
		
		assert(False) #this should never be reached
	
	@staticmethod
	#TODO#Implement
	def hardAI(gameBoard):
		#Eventually will Try all possible moves and selects the one with the most win scenarios
		print "HardAI: not yet implemented"
		return Aikisolver.mediumAI(gameBoard)
	
	@staticmethod
	#find all possible moves for one piece
	def generateEligible(gameBoard, num = "NULL"):
		#TODO#make sure the AI knows where a piece moves to so it 
		if (num == "NULL"):
			num = gameBoard.selectedPiece
		if (not gameBoard.currentBlackLayout[num] == "NULL"):
			turn = "Black"
		else:
			turn = "White"

		#Inserting Colored pieces into the list
		eligible = gameBoard.currentBlackLayout[:]
		for index, item in enumerate(gameBoard.currentWhiteLayout):	
			if (item != "NULL"):
				eligible[index] = item

		#print "selectedPieceColor", eligible[gameBoard.selectedPiece], " -> ", gameBoard.selectedPiece
		eligible[gameBoard.selectedPiece] = "NULL" #AI: makes sure that the place a piece moved out of is considerd
		eligible[num] = "GOOD"
		
		#Unprofessionally determines which positions are valid.
		#TODO#Some of the Black and White specific code could be aggregated by multiplying the indices by '-1' 
		if (turn == "Black"):
			#looks for viable moves above num
			i = 0
			#this algorithm relies on the fact that every 7th space from the origin is on the diagonal, etc.
			#num%8 is the position along the row(0-7). it can iterate this may times before it hits a wall
			#7-num/8 is the number of times it can iterate before hitting the ceiling
			while (i < num%8) and (i < 7-num/8) and (eligible[i*7+num] == "GOOD"): 	
				i = i + 1
				#checks every 7th to make sure its not occupied.
				if (eligible[i*7+num] == "NULL"):
					if (gameBoard.currentSumoLayout[num] == "NULL") or ((gameBoard.currentSumoLayout[num] == "Black") and (i <= 5)) or ((gameBoard.currentSumoLayout[num] == "SuperBlack") and (i <= 3)):
						#not a sumo or is but within distance limit
						eligible[i*7+num] = "GOOD"	

			i = 0
			while (i < 7-num/8) and (eligible[i*8+num] == "GOOD"):			
				i = i + 1				
				if (eligible[i*8+num] == "NULL"):
					if (gameBoard.currentSumoLayout[num] == "NULL") or ((gameBoard.currentSumoLayout[num] == "Black") and (i <= 5)) or ((gameBoard.currentSumoLayout[num] == "SuperBlack") and (i <= 3)):
						eligible[i*8+num] = "GOOD"

			i = 0
			while (i < 7-num%8) and (i < 7-num/8) and (eligible[i*9+num] == "GOOD"):
				i = i + 1		
				if (eligible[i*9+num] == "NULL"):
					if (gameBoard.currentSumoLayout[num] == "NULL") or ((gameBoard.currentSumoLayout[num] == "Black") and (i <= 5)) or ((gameBoard.currentSumoLayout[num] == "SuperBlack") and (i <= 3)):
						eligible[i*9+num] = "GOOD"
			
			#looks for a Sumo Push - if the selected piece is a sumo and has a non sumo enemy piece directly in front with space to push. 
			#(will overwrite good if there is no piece directly in front)
			if (gameBoard.currentSumoLayout[num] != "NULL") and (num <= 47):
				#Single Sumo Push
				if (gameBoard.currentWhiteLayout[num+8] != "NULL") and ((gameBoard.currentSumoLayout[num+8] == "NULL") or (gameBoard.currentSumoLayout[num] == "SuperBlack")) and (eligible[num+16] == "NULL"):
					eligible[num+8] = "GOOD"

				elif (gameBoard.currentSumoLayout[num] == "SuperBlack") and (num <= 39):					
					#Double Sumo Push
					if (gameBoard.currentWhiteLayout[num+8] != "NULL") and (gameBoard.currentWhiteLayout[num+16] != "NULL") and (gameBoard.currentSumoLayout[num+8] != "SuperWhite") and (gameBoard.currentSumoLayout[num+16] != "SuperWhite") and (eligible[num+24] == "NULL"):
						eligible[num+8] = "GOOD"
				
		else :
			#looks for viable moves below num
			i = 0
			#7-num%8 is the position along the row(0-7). it can iterate this may times before it hits a wall
			#num/8 is the number of times it can iterate before hitting the floor
			while (i < 7-num%8) and (i < num/8) and (eligible[num-i*7] == "GOOD"): 	
				i = i + 1
				if (eligible[num-i*7] == "NULL"):
					if (gameBoard.currentSumoLayout[num] == "NULL") or ((gameBoard.currentSumoLayout[num] == "White") and (i <= 5)) or ((gameBoard.currentSumoLayout[num] == "SuperWhite") and (i <= 3)):
						eligible[num-i*7] = "GOOD"	

			i = 0
			while (i < num/8) and (eligible[num-i*8] == "GOOD"):			
				i = i + 1				
				if (eligible[num-i*8] == "NULL"):
					if (gameBoard.currentSumoLayout[num] == "NULL") or ((gameBoard.currentSumoLayout[num] == "White") and (i <= 5)) or ((gameBoard.currentSumoLayout[num] == "SuperWhite") and (i <= 3)):
						eligible[num-i*8] = "GOOD"

			i = 0
			while (i < num%8) and (i < num/8) and (eligible[num-i*9] == "GOOD"):	
				i = i + 1		
				if (eligible[num-i*9] == "NULL"):
					if (gameBoard.currentSumoLayout[num] == "NULL") or ((gameBoard.currentSumoLayout[num] == "White") and (i <= 5)) or ((gameBoard.currentSumoLayout[num] == "SuperWhite") and (i <= 3)):
						eligible[num-i*9] = "GOOD"

			#looks for a Sumo Push
			if (gameBoard.currentSumoLayout[num] != "NULL") and (num >= 16):
				#Single Sumo Push
				if (gameBoard.currentBlackLayout[num-8] != "NULL") and ((gameBoard.currentSumoLayout[num-8] == "NULL") or (gameBoard.currentSumoLayout[num] == "SuperWhite")) and (eligible[num-16] == "NULL"):
					eligible[num-8] = "GOOD"
			
				elif (gameBoard.currentSumoLayout[num] == "SuperWhite") and (num >= 24):
					#Double Sumo Push
					if (gameBoard.currentBlackLayout[num-8] != "NULL") and (gameBoard.currentBlackLayout[num-16] != "NULL") and (gameBoard.currentSumoLayout[num-8] != "SuperBlack") and (gameBoard.currentSumoLayout[num-16] != "SuperBlack") and (eligible[num-24] == "NULL"):
						eligible[num-8] = "GOOD"
		
		#so that the selected piece is not marked.
		eligible[num] = "BAD"

		return eligible
		
#end of class Aikisolver

#Used to create and handle server/game connections
class NetworkConnection():

	import socket
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
		self.challengeTimeout = 15
		self.connectionStatus = "Bad"
		self.callBack = False
		self.killSeekLoop = True
		self.killMoveLoop = True
		self.lobbySock = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
		self.lobbySock.settimeout(3)
		try : 
			self.lobbySock.connect((serverAddress , serverPort))
			self.lobbySock.send("ver="+version)
			string = self.lobbySock.recv(1024)
			if (string[:3] == "ver"):
				self.connectionStatus = "OldVersion="+string[4:]
			else :
				self.connectionStatus = "Server"
				self.localIP = string[8:]
				#print "ip = "+ string[8:]
		
		except :
			#pass
			print "Server not found"			

	#Platform-Specific way to notify the GUI of events
	def callBackActivate(self):
		self.callback = True
		self.callBackWidget.activate()
		#if (platform.system() == "Windows"):
			#pass #TODO# windows specific actions
		#else :
			#pass #TODO#make this for for Linux, etc
	
	#Retrieves the list of currently seeking People from the server
	def getList( self ):
		try :
			self.lobbySock.send("gimme da list bro!")
			seekList = []
			while (True):
				#print "more data coming"
				string = self.lobbySock.recv(1024)
				if (string == "Done"):
					#print "Done Receiving"
					break
				#print "appending: ", string
				seekList.append(string)
				self.lobbySock.send("OK")
		except :
			print "list retrieve failed"
			seekList = ["Please Refresh",""]
		return seekList
	
	#Starts a "Server Loop" that waits for a game connection
	def seekOpponent(self, name):
		try:
			if (self.killSeekLoop):
				#set client's name
				self.name = name
				self.lobbySock.send("name="+name)
				print "threading seek process..."
				##self.challengeLock = threading.Lock()
				##self.challengeLock.acquire()
				self.servSock = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
				self.servSock.bind(('', gamePort))
				self.servSock.listen(1)
				self.servSock.settimeout(5)
				threading.Thread(target=self.seekLoop, args=()).start()
				return True
			else :
				pass
				print "already seeking"
				return False
		except self.socket.error :
			print "Failed, Socket Still in use!"
			return False
		except :
			print "oops! seek init failed..."
			return False

	#"Server Loop" that waits for a game connection then notifies the main GUI
	def seekLoop(self):
		#waiting for remote user to issue challenge
		print "Waiting for Opponent..."
		self.killSeekLoop = False
		while (not self.killSeekLoop):
			try :
				self.connectionStatus = "awaiting challenge"
				(self.gameSock, self.address) = self.servSock.accept()
				print "challenged!!"
				#return Signal
				self.connectionStatus = "challenge received"
				self.callBackActivate()
				##self.challengeLock.acquire()

				break
			except:
				pass
				#print "accept timed out"
				
		print "seek ended."
		self.killSeekLoop = True
		
	def cancelSeekLoop(self):
		print "Canceling seek..."
		self.lobbySock.send("name=") # removes the name from the list
		self.connectionStatus = "Server"
		self.killSeekLoop = True

	#issue challenge and wait for the potential opponent to respond to your challenge
	def challenge(self, ip):
		self.killSeekLoop = True
		print "issued challenge to IP: ", ip
		self.connectionStatus = "issuing challenge"
		threading.Thread(target=self.challengeThread, args=(ip, "stub")).start()

	#Waits for a challenge Response
	def challengeThread(self, ip, stub):
		try :
			self.gameSock = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
			self.gameSock.settimeout(self.challengeTimeout)
			self.gameSock.connect((ip , gamePort))
			string = self.gameSock.recv(1024)
			print "re: ", string
			if (string == "challenge accepted"):
				self.connectionStatus = "challenge accepted"
				print "challenge accepted!"
			else :
				self.gameSock.shutdown(self.socket.SHUT_RDWR)
				self.gameSock.close()
				self.connectionStatus = "Server"
				print "challenge rejected."
		
		except :
			try :
				self.gameSock.shutdown(self.socket.SHUT_RDWR)
				self.gameSock.close()
			except :
				pass
			self.connectionStatus = "Server"
			print "challenge ignored."
			
		self.callBackActivate()
		
	#reply to the remote user who challenged you
	def answerChallenge(self, accept, localColor):
		if (accept):
			print "challenge accepted!"
			if (self.connectionStatus == "challenge received"):
				self.gameSock.send("challenge accepted")
			self.connectionStatus = "Game"
			self.disconnectServer()
			self.gameSock.settimeout(5)
			if (localColor == "White"):
				threading.Thread(target=self.moveLoop, args=()).start() 
			##self.challengeLock.release()
		else :
			#challenge declined... seek must be restarted
			print "challenge declined."
			self.gameSock.send("challenge declined")
			self.gameSock.shutdown(self.socket.SHUT_RDWR) 
			self.gameSock.close()
			threading.Thread(target=self.seekLoop, args=()).start()
	
	#Used by the GUI to tell why it was just called 
	def status( self ):
		return self.connectionStatus

	#Waits for the the opponent to sent their move
	def moveLoop(self):
		#print "starting move loop..."
		self.killMoveLoop = False
		i = 0
		while (not self.killMoveLoop):
			try :
				string = self.gameSock.recv(1024)
				#print "received: ", string
				if (string[:4] == "Move"):
					self.recentMove = string[5:]
					self.callBackActivate()
				elif (string[:4] == "Turn"):
					#print "Its the local players turn."
					break
				elif (string[:4] == "Refo"):
					self.connectionStatus = string
					self.callBackActivate()
				else : 
					print "something got messed up while waiting for the remote move..."
					self.disconnectGame()
					self.callBackActivate()
					break
					
			except self.socket.timeout: 
				#timeouts are perfectly normal, it means the connection is a live but not sending
				print "Still waiting for the remote move..."
			except : 
				#print "Non-fatal Network Error..."
				if (i >= 10):
					#this many errors means the connection was closed. one or two errors can happen
					print "Remote Game Connection Lost."
					self.disconnectGame()
					self.callBackActivate()
				else :
					i = i +1

		#print "move loop ended..."

	#Used by the GUI to find out what the remote players move was
	def getMove(self):
		return int(self.recentMove)
		
	#Tells the opponent what you move was		
	def sendMove( self, pos, turnOver ):
		try:
			#print "Sending Move: ", pos
			self.gameSock.send("Move="+str(pos))
			if (turnOver):
				#let the remote player know its their turn
				self.gameSock.send("Turn!")
				#wait for response
				threading.Thread(target=self.moveLoop, args=()).start() 
		except :
			#TODO#recover gracefully
			print "Fatal Network Error!"
	
	#Tells the opponent how to reform the board for the next match		
	def reform( self, reformType ):
		self.gameSock.send("Reform="+reformType)
		threading.Thread(target=self.moveLoop, args=()).start()
	
	def disconnectServer(self): #used to properly disconnect from the lobby
		self.killSeekLoop = True
		try :
			self.lobbySock.close()
		except : 
			print "server disconnect failed."

	def disconnectGame(self):
		self.killMoveLoop = True
		self.connectionStatus = "Dead"
		try :
			self.gameSock.close()
			
		except : 
			print "game disconnect failed."
	
#end of class: 	NetworkConnection
	
	
class GameGui:
	
	def __init__( self ):
		#loads the GUI file
		self.builder = gtk.Builder()
		self.builder.add_from_file(pwd+"/GUI/main.ui")
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
			"on_callBack_activate" : self.callBack,
			
			#Main Window
			"on_gameWindow_destroy" : self.quit,
			"tile_press_event" : self.tilePressed,
			"on_sendButton_clicked" : self.sendChat,

			#Toolbar
			"on_newGameToolButton_clicked" : self.newGameDialog,
			"on_undoToolButton_clicked" : self.undo,
			"on_saveToolButton_clicked" : self.save,
			"on_showMovesToolButton_toggled" : self.toggleMoves,
			"on_helpToolButton_clicked" : self.help,
			"on_aboutToolButton_clicked" : self.about,

			#New Game Window
			"on_newGameOKButton_clicked" : self.startNewGame,
			"on_newGameCancelButton_clicked" : self.newGameDialogHide,

			#Lobby Window
			"on_lobbySeekButton_clicked" : self.seekNetworkGame,
			"on_lobbyRefreshButton_clicked" : self.lobbyRefresh,
			"on_lobbyCancelButton_clicked" : self.lobbyCancel,
			"on_lobbyChallengeButton_clicked" : self.issueChallenge,
			"on_seekTreeView_focus_in_event" : self.treeViewFocus,
			"on_hostName_focus_in_event" : self.seekButtonFocus ,
			
			#challenge/waiting Window
			"on_yesChallengeButton_clicked" : self.startNetworkGame,
			"on_noChallengeButton_clicked" : self.declineChallenge,
			"on_waitingStopButton_clicked" : self.closeWaitingDialog,
			
			#Grats/Sorry Window
			"on_reform_clicked" : self.gratsHide,
			
			#saveFileChooser
			"on_saveFileButton_clicked" : self.save,
			
			#Update Dialog
			"on_updateYesButton_clicked" : self.updateDialog,
			"on_updateNoButton_clicked" : self.updateDialog
			
		}
		self.builder.connect_signals( dic )
		
	def test(self, widget):
		self.updateDialog()
		#pos = self.builder.get_object("gameWindow").get_position()
		#self.builder.get_object("waitingDialog").move(pos[0]+25, pos[1]+75)
		#self.builder.get_object("waitingDialog").present()
		#self.killProgressBar = False
		#threading.Thread(target=self.progressLoop, args=(self.builder.get_object("waitingProgressBar"),15)).start()
	
	def stub(self, widget, event = "NULL"):
		print "Feature not yet implemented."

	#For intercepting the "delete-event" and instead hiding
	def widgetHide(self, widget, trigeringEvent):
		if (widget == self.builder.get_object("gratsDialog")):
			self.gratsHide()
		elif (widget == self.builder.get_object("waitingDialog")):
			self.closeWaitingDialog()
			
		widget.hide()
		return True

	def quit(self, widget = "NULL"):
		self.killProgressBar = True
		try:
			self.connection.disconnectServer()
		finally :	
			try :
				self.connection.disconnectGame()
			finally :
				sys.exit(0)

	def tilePressed(self, widget, trigeringEvent):
		#print "Pressed Button: ", widget.get_child().get_name()
		#pass the board the gameTable so it can mess with the images.
		if not (self.board.winner): 
			if (self.gameType[:5] == "Local") or (self.board.turn == self.localColor):
				moveSuccess = self.board.selectSquare(int(widget.get_child().get_name()))
				#moveSuccess is true if the move is valid; prevents sending illegitimate moves.
				#print "Move Success: "+str(moveSuccess)
				if (self.gameType == "Network"):
					self.connection.sendMove(int(widget.get_child().get_name()), (moveSuccess and (not self.board.winner)))
				if (moveSuccess):
					if (self.gameType == "Network"):
						self.builder.get_object("statusLabel").set_text("It's the Remote Players turn...")
					elif (self.gameType == "Local-AI"):
						self.builder.get_object("statusLabel").set_text("It's Your Turn! ("+self.board.turn+")")
					self.builder.get_object("undoToolButton").set_sensitive(True)
					self.builder.get_object("saveToolButton").set_sensitive(True)
						
			#Else: wait for remote player to select a piece	

		if (self.board.winner == True): 
			self.announceWinner()

	def announceWinner(self):
		#TODO# this should be changed to "White" it is just not working right now because the AI featue is not implemented
		if ((self.gameType == "Network") and (self.board.turn != self.localColor)) or ((self.gameType == "Local-AI") and (self.board.turn == "White")):
			#the remote/AI player won
			pos = self.builder.get_object("gameWindow").get_position
			#TODO#Fix the crash the next line causes
			#self.builder.get_object("sorryDialog").move(pos[0]+25, pos[1]+75)
			self.builder.get_object("sorryLabel").set_text("Sorry, You lost....")
			self.builder.get_object("sorryDialog").present()
		
		else :
			#a local player won
			#print "color: "+self.board.turn+", type: "+self.gameType
			self.builder.get_object("gratsLabel").set_text("Congratulations "+self.board.turn+",\n        You Win!!")
			pos = self.builder.get_object("gameWindow").get_position
			#self.builder.get_object("gratsDialog").move(pos[0]+25, pos[1]+75)
			self.builder.get_object("gratsDialog").present()

		self.builder.get_object("scoreLabel").set_text("Black: "+str(self.board.blackWins)+" | White: "+str(self.board.whiteWins))
		
	def toggleMoves(self, widget):
		self.board.toggleShowMoves(self.builder.get_object("showMovesToolButton").get_active())
		
	def newGameDialog(self, widget="NULL"):
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("newGameDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("newGameDialog").present()

	def newGameDialogHide(self, widget):
		self.builder.get_object("newGameDialog").hide()
	
	def startNewGame(self, widget="NULL"): 
		#hide chatFrame
		self.builder.get_object("chatFrame").hide()
		self.builder.get_object("undoToolButton").set_sensitive(False)
		self.builder.get_object("saveToolButton").set_sensitive(False)
		if (self.builder.get_object("networkGameRadioButton").get_active()):
			#Starting a new network Game (starting to find)
			#Hand the NetworkConnection class a way to callback.
			if (platform.system() == "Windows"): #FIXME#these should use "callBackWidget"
				self.connection = NetworkConnection(self.builder.get_object("lobbyRefreshButton"))
			else :		
				self.connection = NetworkConnection(self.builder.get_object("callBackButton"))

			if (self.connection.status() == "Server"):
				print "Found Server!"
			
				self.newGameDialogHide( self )
				pos = self.builder.get_object("gameWindow").get_position()
				self.builder.get_object("lobbyDialog").move(pos[0]+25, pos[1]+75)
				self.builder.get_object("lobbyDialog").present()
				self.lobbyRefresh() #add items to list
			elif (self.connection.status()[:10] == "OldVersion"):
				#Update To Newest Version
				print "You have an old version and must update to play online!"
				self.updateDialog()
				
			#Else, unable to reach server
	
		else:
			
			#passing the method directly prevents having to check difficulty again later
			if (self.builder.get_object("EasyAIRadioButton").get_active()):
				self.gameType = "Local-AI"
				self.board = GameBoard(self.builder.get_object("gameTable"), self.builder.get_object("statusLabel"), self.builder.get_object("enableAnimationsBox").get_active(), Aikisolver.easyAI)
			elif (self.builder.get_object("MediumAIRadioButton").get_active()):
				self.gameType = "Local-AI"
				self.board = GameBoard(self.builder.get_object("gameTable"), self.builder.get_object("statusLabel"), self.builder.get_object("enableAnimationsBox").get_active(), Aikisolver.mediumAI)
			elif (self.builder.get_object("HardAIRadioButton").get_active()):
				self.gameType = "Local-AI"
				self.board = GameBoard(self.builder.get_object("gameTable"), self.builder.get_object("statusLabel"), self.builder.get_object("enableAnimationsBox").get_active(), Aikisolver.hardAI)
			elif (self.builder.get_object("openFileRadioButton").get_active()):
				print "OpenFile: Feature not yet implemented"
				return
			else:#if (self.builder.get_object("localMultiGameRadioButton").get_active()):
				#Starting a new local game
				self.gameType = "Local"
				self.board = GameBoard(self.builder.get_object("gameTable"), self.builder.get_object("statusLabel"), self.builder.get_object("enableAnimationsBox").get_active())

			self.newGameDialogHide( self )
			self.board.reset()
			if (self.gameType == "Local-AI"):
				self.builder.get_object("statusLabel").set_text("It's Your Turn! ("+self.board.turn+")")
			self.builder.get_object("scoreLabel").set_text("Black: 0 | White: 0")
	

	def lobbyRefresh(self, widget="NULL"):
		#this button doubles as a call back for self.connection
		if (self.connection.callBack == True):
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
			else :
				#FIXME#highlight the top element
				self.builder.get_object("seekTreeView").grab_focus()
				
	def treeViewFocus(self, wigdet, event):
		self.builder.get_object("lobbyChallengeButton").grab_focus()
		
	def seekButtonFocus(self, wigdet, event):
		self.builder.get_object("lobbySeekButton").grab_default()

	def lobbyCancel(self, widget):
		self.connection.disconnectServer()
		self.builder.get_object("lobbyDialog").hide()
		self.builder.get_object("hostName").set_sensitive(True)
		self.builder.get_object("seekButtonPlay").set_visible(True)
		self.builder.get_object("seekButtonStop").set_visible(False)
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("newGameDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("newGameDialog").present()

	def seekNetworkGame(self, widget):
		print "Status: "+self.connection.status()
		print "Clicked Seek."
		string = self.builder.get_object("hostName").get_text()
		
		if (string != "") and (self.connection.status() == "Server"): #not seeking...
			#try :
			worked = self.connection.seekOpponent(string)
			#except :
				#Ends a currently running game
				#self.connection.disconnectGame()
				#self.connection.seekOpponent(string)
			
			if (worked):
				self.builder.get_object("hostName").set_sensitive(False)
				self.builder.get_object("seekButtonPlay").set_visible(False)
				self.builder.get_object("seekButtonStop").set_visible(True)
				
		elif (string != ""): #already seeking...
			self.builder.get_object("hostName").set_sensitive(True)
			self.builder.get_object("seekButtonPlay").set_visible(True)
			self.builder.get_object("seekButtonStop").set_visible(False)
			self.connection.cancelSeekLoop()
		
		self.lobbyRefresh()

	def issueChallenge(self, widget):
		(model, iter) = self.builder.get_object("seekTreeView").get_selection().get_selected()
		#name = self.seekStore.get_value(iter, 0)
		ip = self.seekStore.get_value(iter, 1)
		if (ip != self.connection.localIP): #makes sure your not trying to challenge yourself
			pos = self.builder.get_object("gameWindow").get_position()
			self.builder.get_object("waitingDialog").move(pos[0]+25, pos[1]+75)
			self.builder.get_object("waitingDialog").present()
			threading.Thread(target=self.progressLoop, args=(self.builder.get_object("waitingProgressBar"),self.connection.challengeTimeout)).start()
			#this cancels the seek, the button should be re-enabled
			self.builder.get_object("hostName").set_sensitive(True)
			self.builder.get_object("seekButtonPlay").set_visible(True)
			self.builder.get_object("seekButtonStop").set_visible(False)
			self.connection.challenge(ip)
			
	def closeWaitingDialog(self, widget = "NULL", event = "NULL"):
		self.killProgressBar = True
		self.builder.get_object("waitingDialog").hide()
	
	def callBack(self, widget="Null"):
		self.connection.callBack = False
		if (self.connection.status() == "challenge received"):
			#challenge received from a remote player
			self.recieveChallenge()
		elif (self.connection.status() == "challenge accepted"):
			#the remote player accepted the locally issued challenge
			self.closeWaitingDialog(self)
			self.localColor = "White" #this ensures that the player who is challenged goes first
			self.startNetworkGame()
		elif (self.connection.status() == "Server"):
			#Challenge Refused
			self.closeWaitingDialog(self)
			self.builder.get_object("sorryLabel").set_text("Your challenge was refused.")
			self.builder.get_object("sorryDialog").present()
			
		elif (self.connection.status() == "Game"):
			#moves a piece for the remote player
			moveSuccess = self.board.selectSquare(self.connection.getMove())
			if (moveSuccess): 
				self.builder.get_object("statusLabel").set_text("It's Your Turn! ("+self.board.turn+")")
			if (self.board.winner == True): 
				self.announceWinner()
		elif (self.connection.status()[:4] == "Refo"):
			self.builder.get_object("gratsDialog").hide()
			self.builder.get_object("sorryDialog").hide()
			self.board.reset(self.connection.status()[7:])
			self.builder.get_object("statusLabel").set_text("It's Your Turn! ("+self.board.turn+")")
			self.connection.connectionStatus = "Game" #Next time it receives something it knows its a move and not a reform.
		elif (self.connection.status()[:4] == "Chat"):
			#Display message
			self.builder.get_object("chatBuffer").insert(self.builder.get_object("chatBuffer").get_end_iter(), "\n"+self.connection.status()[5:])
			self.builder.get_object("chatVAdjustment").set_value(self.builder.get_object("chatVAdjustment").get_upper())
		elif (self.connection.status() == "Dead"):
			self.builder.get_object("statusLabel").set_text("Remote Game Connection Lost.")
			self.newGameDialog()						
	
	def recieveChallenge(self):
		#displays the challenge dialog
		print "Challenge Received!"
		self.localColor = "Black" #this ensures that the player who is challenged goes first
		opponentIP = self.connection.address[0]
		self.builder.get_object("challengeLabel").set_text("You have been challenged by a player at: "+ opponentIP +" !")
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("challengeDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("challengeDialog").present()

	def declineChallenge(self, widget):
		#TODO# implement failsafe
		#worked = self.connection.answerChallenge(False, "Null")
		self.connection.answerChallenge(False, "Null")
		self.builder.get_object("challengeDialog").hide()

	def startNetworkGame(self, widget="Null"): #called when a local/remote user accepts a challenge
		self.connection.answerChallenge(True, self.localColor)
		print "Your Color: "+self.localColor
		self.gameType = "Network"
		self.builder.get_object("challengeDialog").hide()
		self.builder.get_object("lobbyDialog").hide()
		self.board = GameBoard(self.builder.get_object("gameTable"), self.builder.get_object("statusLabel"), self.builder.get_object("enableAnimationsBox").get_active())
		self.board.reset()
		self.builder.get_object("scoreLabel").set_text("Black: 0 | White: 0")
		#TODO#show chatFrame
		#self.builder.get_object("chatFrame").show()
		if (self.board.turn == self.localColor):
			self.builder.get_object("statusLabel").set_text("It's Your Turn! ("+self.board.turn+")")
		else :
			self.builder.get_object("statusLabel").set_text("It's the Remote Players turn...")

	def undo(self, widget):
		self.builder.get_object("undoToolButton").set_sensitive(False)
		self.board.undo()
		
	def save(self, widget):
		if (widget == self.builder.get_object("saveToolButton")):
			pos = self.builder.get_object("gameWindow").get_position()
			self.builder.get_object("saveFileChooser").move(pos[0]-25, pos[1]+75)
			self.builder.get_object("saveFileChooser").present()
			print "Moves: ",self.board.moves 
		elif (widget == self.builder.get_object("cancelSaveButton")):
			self.builder.get_object("saveFileChooser").hide()
		else:
			print "Save: feature not yet implemented"
				

	def help(self, widget):
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("helpDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("helpDialog").present()

	def about(self, widget):
		global version
		self.builder.get_object("aboutDialog").set_version(version)
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("aboutDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("aboutDialog").present()

	def gratsHide(self, widget="NULL", event="NULL"):
		if (widget == self.builder.get_object("sorryOKButton")):
			if (self.gameType == "Local-AI"):
				reformType = "RTL"
				self.builder.get_object("undoToolButton").set_sensitive(False)
				self.board.reset(reformType)
				self.builder.get_object("statusLabel").set_text("It's Your Turn! ("+self.board.turn+")")
			else :
				self.builder.get_object("statusLabel").set_text("Please wait for Remote Player to start the next Round.")
			#no reform necessary because the user lost.
			self.builder.get_object("sorryDialog").hide()
			
			return
		elif (widget == self.builder.get_object("reformLTRButton")):
			reformType = "LTR"
		elif (widget == self.builder.get_object("reformNormalButton")):
			reformType = "Normal"
		else: 
			reformType = "RTL"
		
		self.builder.get_object("undoToolButton").set_sensitive(False)
		self.builder.get_object("gratsDialog").hide()	
		self.board.reset(reformType)
		if (self.gameType == "Network"):
			self.connection.reform(reformType)
			self.builder.get_object("statusLabel").set_text("It's the Remote Players turn...")

	def progressLoop(self, pBar, num):
		num = 20*num
		self.killProgressBar = False
		for i in range(1,num+1):
			if (self.killProgressBar): break
			pBar.set_fraction(float(i)/num)
			time.sleep(0.05)

	def updateDialog(self, widget="NULL", event = "NULL"):
		if (widget == "NULL"):
			#Show updateDialog
			print "showing updateDialog"
			if (os.access(pwd, os.W_OK) and updatesEnabled):
				#Write Permissions emabled on Aikisado.py
				self.builder.get_object("updateOKLabel").show()
				self.builder.get_object("updateImpossibleLabel").hide()
				self.builder.get_object("updateLink").hide()
				self.builder.get_object("updateYesButton").show()
				self.builder.get_object("updateYesButton").grab_focus()
				self.builder.get_object("updateNoButton").show()
				self.builder.get_object("updateOKButton").hide()
				pos = self.builder.get_object("gameWindow").get_position()
				self.builder.get_object("updateDialog").move(pos[0]+25, pos[1]+75)
				self.builder.get_object("updateDialog").present()
			else:
				#TODO#try to Download zip file instead
				#access to the file denied
				self.builder.get_object("updateOKLabel").hide()
				self.builder.get_object("updateImpossibleLabel").show()
				self.builder.get_object("updateLink").show()
				self.builder.get_object("updateYesButton").hide()
				self.builder.get_object("updateNoButton").hide()
				self.builder.get_object("updateOKButton").show()
				self.builder.get_object("updateOKButton").grab_focus()
				pos = self.builder.get_object("gameWindow").get_position()
				self.builder.get_object("updateDialog").move(pos[0]+25, pos[1]+75)
				self.builder.get_object("updateDialog").present()

		elif (widget == self.builder.get_object("updateYesButton")):
			#threading.Thread(target=aikisadoUpdate, args=()).start()
			aikisadoUpdate()
			self.quit()

		else :
			print "hiding UpdateDialog"
			self.builder.get_object("updateDialog").hide()


	def sendChat(self, widget):
		self.builder.get_object("chatBuffer").insert(self.builder.get_object("chatBuffer").get_end_iter(), "\n"+self.builder.get_object("chatEntry").get_text())
		self.builder.get_object("chatEntry").set_text("")
		self.builder.get_object("chatVAdjustment").set_value(self.builder.get_object("chatVAdjustment").get_upper())
			
#end of class: GameGUI

	
def aikisadoUpdate():
	#TODO# Make aikisado restart after update
	import urllib2
	import zipfile
	import shutil
	
	#Download File
	print "Downloading file..."
	zipFileURL = urllib2.urlopen("http://downloads.sourceforge.net/project/aikisado/AikisadoUpdate.zip")
	zipFile = open(pwd+"/AikisadoUpdate.zip", "wb")
	zipFile.write(zipFileURL.read())
	zipFile.close()
	print "Download Complete!"

	#Delete old update backup file
	shutil.rmtree(pwd+"/OldVersion/", True)
	
	#Backup Previous Version
	shutil.copytree(pwd, pwd+"/OldVersion/")

	#UnZip File over writing the previous version
	#The zipfile should have the Aikisado.pyw in the root dir
	zipFileObject = zipfile.ZipFile(pwd+"/AikisadoUpdate.zip")
	for name in zipFileObject.namelist():
		if name.endswith('/'):
			if ( not os.path.exists(pwd+"/"+name)):
				os.mkdir(pwd+"/"+name)
		else:
			outfile = open(os.path.join(pwd, name), 'wb')
			outfile.write(zipFileObject.read(name))
			outfile.close()

	#Remove Zipfile
	os.remove(pwd+"/AikisadoUpdate.zip")
	if (platform.system() == "Windows"):
		os.execl(pwd+"\\Aikisado.py", "0")
	else:
		os.execl(pwd+"/Aikisado.py", "0")
#End of Method aikisadoUpdate 

def start(): #basically main
	gobject.threads_init() #Makes threads work. Formerly "gtk.gdk.threads_init()", but windows really hated it.
	gui = GameGui()
	gtk.main()

if __name__ == "__main__": #so main wont execute when this module (Aikisado) is imported
	start()
