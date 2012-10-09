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

import os
import re
import sys
import time
import site
import copy
import Queue
import random
import gobject
import platform
import threading
import ConfigParser

try:
	import pygtk
	pygtk.require("2.0")
except:
	print "Aikisado: Missing Pygtk"
	
try:
	import gtk
except:
	print("Aikisado: GTK Not Available")
	sys.exit(1)

version = "0.3.6.3"
serverPort = 2306 #TCP# 
gamePort = 2307 #TCP# Forward this port on your router
tileSize = 48 #Do not touch!
TileSet = "Original"

#Holds all of the information to specify the state of a game
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

	#Initializes the values that reset shouldn't
	def __init__( self, table, status, gameType=None, filename=None):
		#Stores a local list of the eventBoxes (tiles)
		#The tiles at the bottom right corner are first
		self.table = table.get_children()
		#Keeps track of the statusLabel
		self.status = status
		self.gameType = gameType
		self.AIMethod = Aikisolver.getMethod(gameType)
		self.moves = []
		#Initialize Lists; [:] makes it a copy instead of a reference.
		self.eligible = self.sumoPieceLayout[:]
		self.currentBlackLayout = self.blackPieceLayout[:]
		self.currentWhiteLayout = self.whitePieceLayout[:]
		self.currentSumoLayout = self.sumoPieceLayout[:]
		self.firstTurn = True
		self.sumoPush = False
		self.turn = "White"
		self.blackWins = 0
		self.whiteWins = 0
		if (filename != None):
			self.loadMoves(filename)
		else :
			if (self.gameType == None):
				self.gameType = "Local"
			self.reset()
		
	#Starts a new round of the game
	def reset( self , mode="Normal" ):
		self.firstTurn = True
		self.winner = False
		self.selectedPiece = -1
		self.eligible = self.sumoPieceLayout[:]
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
		
		#Reformat sumo list to move all of the sumos to their home row
		tempSumoLayout = self.currentSumoLayout[:]
		self.currentSumoLayout = self.sumoPieceLayout[:]
		for index, item in enumerate(tempSumoLayout):
			if (item == "Black") or (item == "SuperBlack"):
				#Qualify the new piece in the position based on the color of the piece in the old layout
					#and the index of that piece in the new layout
				#TempBlackLayout[index] is the color of the piece
				#self.currentBlackLayout.index() finds the index of a specific color
				self.currentSumoLayout[self.currentBlackLayout.index(tempBlackLayout[index])] = item
			elif (item == "White") or (item == "SuperWhite"): 
				self.currentSumoLayout[self.currentWhiteLayout.index(tempWhiteLayout[index])] = item
					
		#Swap turn so the looser goes first this time
		if (self.turn == "White") or (self.AIMethod != None):
			self.turn = "Black" #Player always goes first vs AI
			self.cursorPos = 3 #Same starting position as a king in chess =)
		else :
			self.turn = "White"
			self.cursorPos = 59

		self.status.set_text("Player Turn: "+self.turn)
		
		#Save initial state for self.undo
		self.previousTurn = self.turn
		self.previousSelectedPiece = self.selectedPiece
		self.previousBlackLayout = self.currentBlackLayout[:]
		self.previousWhiteLayout = self.currentWhiteLayout[:]
		self.previousSumoLayout = self.currentSumoLayout[:]

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
				else :
					self.placePiece( self.selectedPiece, self.currentWhiteLayout[self.selectedPiece], self.turn )
			#Verify there is a valid piece on the selected square
			if (self.turn == "Black" and self.currentBlackLayout[num] != "NULL" and self.currentWhiteLayout[num] == "NULL"):
				#The Black Player has selected a Black Piece
				self.selectedPieceColor = self.currentBlackLayout[num]
				self.selectedPiece = num
				self.determineMoves()
				self.markSelected()
				self.cursorPos = num
				#return True
			elif (self.turn == "White" and self.currentWhiteLayout[num] != "NULL" and self.currentBlackLayout[num] == "NULL"):
				#The White Player has selected a White Piece
				self.selectedPieceColor = self.currentWhiteLayout[num]
				self.selectedPiece = num
				self.determineMoves()
				self.markSelected()
				self.cursorPos = num
				#return True
			elif (self.selectedPiece >= 0): 			
				#The user has clicked on a blank square after selecting a piece
				if (self.eligible[num] == "GOOD"):
					self.firstTurn = False
					self.makeMove( num )
					if (self.AIMethod != None): #if there is an AI player
						self.makeMove(self.AIMethod(self))
					return True
				else :
					#needed to keep the selected piece highlighted when the user clicks on an invalid square
					self.markSelected() 
			#Else, there is no initial piece selected and therefore nothing happens
		else :
			#The User is selecting a destination (not firstTurn)
			if (self.eligible[num] == "GOOD"):
				self.previousTurn = self.turn
				self.previousSelectedPiece = self.selectedPiece
				self.previousBlackLayout = self.currentBlackLayout[:]
				self.previousWhiteLayout = self.currentWhiteLayout[:]
				self.previousSumoLayout = self.currentSumoLayout[:]
				ret = self.makeMove( num )
				if (ret and (not self.AIMethod == None) and (not self.winner) and self.turn == "White"): #turn = black after sumo push.
					self.makeMove(self.AIMethod(self))

				return ret
			else :
				#peek at the moves
				pass
				#print "peeking"
				#eligible = Aikisolver.generateEligible(self, num, self.selectedPiece)
				#self.markEligible(eligible)
				
			#Else, the user selected a non-blank square and nothing will happen
			
		return False
			
	#Move the selectedPiece to num, choose the new selected piece, mark it, and swap turns if necessary
	#Returns: whether or not the players should switch turns
	def makeMove( self, num ):	
		ret = True #return value (if the players switch turns.)
		possibleBonus = 0	
		self.sumoPush = False	
		if (self.turn == "Black") and (self.currentWhiteLayout[num] != "NULL"):
			#Black Sumo Push!
			print "Black Sumo Push!"
			ret = False
			self.sumoPush = True
			self.recordMove("Push", self.selectedPiece, num)
			if (self.currentWhiteLayout[num+8] != "NULL"):
				#Double Push - take all of the below procedures one step further
				self.removePiece(num+8)
				self.currentSumoLayout[num+16] = self.currentSumoLayout[num+8]
				self.placePiece(num+16, self.currentWhiteLayout[num+8], "White")
				self.currentWhiteLayout[num+16] = self.currentWhiteLayout[num+8]
				possibleBonus = 8 #Makes sure that the location of the second pushed piece determines the color of the next move 
			#Make Move
			self.movePiece( self.selectedPiece, num, self.selectedPieceColor, self.turn, +1)
			#Modify current sumo Layout
			self.currentSumoLayout[num+8] = self.currentSumoLayout[num]
			self.currentSumoLayout[num] = self.currentSumoLayout[self.selectedPiece]
			self.currentSumoLayout[self.selectedPiece] = "NULL"		
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
			print "White Sumo Push!"
			ret = False
			self.sumoPush = True
			self.recordMove("Push", self.selectedPiece, num)
			if (self.currentBlackLayout[num-8] != "NULL"):
				#Double Push
				self.removePiece(num-8)
				self.currentSumoLayout[num-16] = self.currentSumoLayout[num-8]
				self.placePiece(num-16, self.currentBlackLayout[num-8], "Black")
				self.currentBlackLayout[num-16] = self.currentBlackLayout[num-8]
				possibleBonus = 8
			#make move
			self.movePiece( self.selectedPiece, num, self.selectedPieceColor, self.turn, -1)
			#Modify current sumo Layout
			self.currentSumoLayout[num-8] = self.currentSumoLayout[num]
			self.currentSumoLayout[num] = self.currentSumoLayout[self.selectedPiece]
			self.currentSumoLayout[self.selectedPiece] = "NULL"
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

						
		else :
			#Determine the possible moves for next turn
			self.determineMoves()
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
			if ((self.AIMethod != None) and self.turn == "White" and skipped):
				self.makeMove(self.AIMethod(self))
			if ((self.AIMethod != None) and self.turn == "White" and self.sumoPush):
				self.makeMove(self.AIMethod(self)) #make the AI move after is pushes
			self.markSelected()
		#end else (no winner)
		self.cursorPos = self.selectedPiece
		return ret #returns true if the players should switch turns

	#Place Piece over existing BG
	def placePiece( self, num, pieceColor, playerColor):
		#GET BG pixbuf
		bg = self.table[num].get_child().get_pixbuf()
		#bg = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/" + self.boardLayout[num] + "BG.png")
		
		#Get Piece pixbuf
		piece = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/"+pieceColor+playerColor+"Piece.png")
		if (self.currentSumoLayout[num] != "NULL"):
			#Get Sumo pixbuf and Composite it onto the Piece
			sumo = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/Sumo"+self.currentSumoLayout[num] + ".png")
			sumo.composite(piece, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
		#Composite Piece Over BG
		piece.composite(bg, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
		#Set the tile to contain the new image
		self.table[num].get_child().set_from_pixbuf(bg)

	#Starts the Animation for the movement of a game piece if enabled
	def movePiece( self, startingPosition, finalPosition, pieceColor, playerColor, push=None):
		if (not push == None):
			if (playerColor == "White"):
				self.placePiece( finalPosition-8, self.currentBlackLayout[finalPosition], "Black" )
			else :
				self.placePiece( finalPosition+8, self.currentWhiteLayout[finalPosition], "White" )
		
		if (enableAnimations):
			#Prepare for the board for animations - (eligible changes the instant the thread starts)
			#go through and unmark everything
			if (showMoves):
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
			self.animationSequence(startingPosition, finalPosition, pieceColor, playerColor, self.currentSumoLayout[finalPosition])
		
		self.removePiece( self.selectedPiece )
		self.placePiece( finalPosition, self.selectedPieceColor, self.turn )
		
	#Animates a piece over the backGround then returns the the board to its normal state
	def animationSequence( self, startingPosition, finalPosition, pieceColor, playerColor, sumo):
		#Declare animation constants
		#timeToCrossOneSquare = 0.08 #0.1875 Will cross the board in 1.5 seconds
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
				tmpPixbuf = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/" + self.boardLayout[pos] + "BG.png")
				tmpPixbuf.composite(backGround, w*tileSize, h*tileSize, tileSize, tileSize, w*tileSize, h*tileSize, 1, 1, gtk.gdk.INTERP_HYPER, 255)
				#set the squares to subpixbufs of the backGround - when the background pixbuf gets updates so does its subpixbufs
				self.table[pos].get_child().set_from_pixbuf(backGround.subpixbuf(w*tileSize, h*tileSize, tileSize, tileSize))
				
		#Add the static pieces to the backGround
		tabooColor = self.boardLayout[finalPosition] #This is needed only for AI games where the next move may appear during animation because both moves modify the board before the animation occurs.
		for index, item in enumerate(hijackedSquares):
			if (item == startingPosition):
				continue
			if (self.currentBlackLayout[item] != "NULL") and (item != finalPosition):
				self.placePiece( item, self.currentBlackLayout[item], "Black" )
			elif (self.currentWhiteLayout[item] != "NULL") and (item != finalPosition) and (self.currentWhiteLayout[item] != tabooColor):
				self.placePiece( item, self.currentWhiteLayout[item], "White" )
		
		#Calc Animation variables
		numberOfFrames = framesPerSquare*(height-1)
		#frameWaitTime = timeToCrossOneSquare / framesPerSquare #1/FPS
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

		piece = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/"+pieceColor+playerColor+"Piece.png")
		if (not sumo == "NULL"):
			#make the piece look like a sumo.
			sumoPix = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/Sumo"+sumo+".png")
			sumoPix.composite(piece, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)	

		#Repeatedly move piece on the master backGround and refresh the widgets
		for i in range(numberOfFrames):
			blankBackGround.composite(backGround, 0, 0, width*tileSize, height*tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
			#print "pos: (",(i*xDisplacement*pixPerFrame)+startingPixel[0],", ",(i*yDisplacement*pixPerFrame)+startingPixel[1],")"
			#(i*xDisplacement*pixPerFrame)+tileSize = the X-position to place the piece 
			piece.composite(backGround, (i*xDisplacement*pixPerFrame)+startingPixel[0], (i*yDisplacement*pixPerFrame)+startingPixel[1], tileSize, tileSize, (i*xDisplacement*pixPerFrame)+startingPixel[0], (i*yDisplacement*pixPerFrame)+startingPixel[1], 1, 1, gtk.gdk.INTERP_HYPER, 255)
			self.table[0].get_parent().queue_draw()
			#time.sleep(frameWaitTime)
			#All events should be processed but this takes too much time on the Pandora
			processGtkEvents()
			
		#Replace the static pieces
		for index, item in enumerate(hijackedSquares):
			self.removePiece(item)
			if (item == startingPosition):
				continue
			if (self.currentBlackLayout[item] != "NULL"):
				self.placePiece( item, self.currentBlackLayout[item], "Black" )
			elif (self.currentWhiteLayout[item] != "NULL"):
				self.placePiece( item, self.currentWhiteLayout[item], "White" )
		
		self.placePiece(finalPosition, pieceColor, playerColor)
		if not (self.winner):
			self.markSelected() #if the selected piece was in the animated area.
			self.markEligible()
		
		
	#Place Eligible Mark over existing Piece/BG
	def markEligible( self, eligible="NULL", nums=None, place=None):
		#Subroutine to place the appropriate graphic down
		def placeMarker(num, color="Black"):
			#GET BG pixbuf
			bg = self.table[num].get_child().get_pixbuf()
			#Get Mark pixbuf	
			if (self.currentBlackLayout[num] != "NULL"):
				mark = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/SumoPushDown.png")
			elif (self.currentWhiteLayout[num] != "NULL"):
				mark = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/SumoPushUp.png")
			else :
				mark = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/EligibleMark"+color+".png") 
			#Composite Mark Over BG
			if (nums != None):
				#composite the image of a number over the square to see its priority.
				print "feature not yet available"
			else:
				mark.composite(bg, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
			#Set the tile to contain the new image
			self.table[num].get_child().set_from_pixbuf(bg)
		#END: placeMarker()
		
		if (eligible == "NULL"):
			eligible = self.eligible
			color = "Black"
		else:
			color = "Grey"
		if (showMoves):
			if (place != None):
				if (eligible[place] == "GOOD"):
					placeMarker(place)
			else :
				for index, item in enumerate(eligible):
					if (item == "GOOD"):
						placeMarker(index, color)

	#Set the BG to the layout default (solid color)
	def removePiece( self, num ):
		#Restores the tile to its original solid BG color
		self.table[num].get_child().set_from_file(pwd+"/GUI/TileSets/"+TileSet+"/"+self.boardLayout[num]+"BG.png")
	
	#Place Brackets over existing Piece/BG 
	def markSelected( self ):
		#GET BG pixbuf
		bg = self.table[self.selectedPiece].get_child().get_pixbuf()
		#Get Mark pixbuf		
		mark = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/SelectedMark.png") 
		#Composite Mark Over BG
		mark.composite(bg, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
		#Set the tile to contain the new image
		self.table[self.selectedPiece].get_child().set_from_pixbuf(bg)

	#fills up eligible[] and places marks.
	def determineMoves( self ):
		num = self.selectedPiece
		#go through and unmark everything
		for index, item in enumerate(self.eligible):
			if (item == "GOOD") or (index == self.cursorPos):
				self.removePiece(index)
				#check to see if you removed a piece
				if (self.currentBlackLayout[index] != "NULL"):
					#This (index) is where the previously selected piece moved to
					#or a Sumo was eligible to push but didn't; remove marker.
					self.placePiece(index, self.currentBlackLayout[index], "Black")
				elif (self.currentWhiteLayout[index] != "NULL"):
					self.placePiece(index, self.currentWhiteLayout[index], "White")
		
		self.eligible = Aikisolver.generateEligible(self)

		self.markEligible()

	#Reverts the board to its previous state.
	def undo(self):
		#print "Turn: ",self.turn,"->",self.previousTurn
		#print "AI: ",self.AIMethod
		#print "sumoPush:",self.sumoPush
		self.turn =	self.previousTurn
		self.selectedPiece = self.previousSelectedPiece
		self.cursorPos = self.selectedPiece
		if (self.turn == "White"):
			if (not self.AIMethod == None):
				self.currentBlackLayout = self.previousBlackLayout[:]
				self.moves.pop()
			if (self.sumoPush):
				self.currentBlackLayout = self.previousBlackLayout[:]
			self.currentWhiteLayout = self.previousWhiteLayout[:]
			self.selectedPieceColor = self.currentWhiteLayout[self.selectedPiece]
			self.moves.pop()
		if (self.turn == "Black"):
			if (not self.AIMethod == None):
				self.currentWhiteLayout = self.previousWhiteLayout[:]
				self.moves.pop()
			if (self.sumoPush):
				self.currentWhiteLayout = self.previousWhiteLayout[:]
			self.currentBlackLayout = self.previousBlackLayout[:]
			self.selectedPieceColor = self.currentBlackLayout[self.selectedPiece]
			self.moves.pop()

		self.selectedPiece = self.previousSelectedPiece
		self.currentSumoLayout = self.previousSumoLayout[:]
		self.status.set_text("Player Turn: "+self.turn)
		self.eligible = Aikisolver.generateEligible(self)
		
		#print "Piece: ",self.selectedPiece,"(",self.selectedPieceColor,")"
		
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
			
		else :
			self.markSelected()
			self.markEligible()

	#Saves a string in self.moves describing an action.
	def recordMove(self, moveType, fromSpace, toSpace):
		self.moves.append(moveType+self.turn+": "+str(fromSpace)+"("+self.boardLayout[fromSpace]+")"+" to: "+str(toSpace)+"("+self.boardLayout[toSpace]+")")

	#Private function to simulate and confirm the moves in a file.
	def loadMoves(self, filename):
		f = iter(open(filename))
		gameType = self.gameType #gameType will = None if the user has not selected an override while loading
		self.gameType = "Local" #Needs to be local for the playt-hrough to work (maybe)
		self.AIMethod = None
		#parse the rest of the file for moves.
		for index, line in enumerate(f):
			if (line.startswith("Move")):
				nums = re.split('[a-zA-Z() :]+',line)#Python 2.7: ,flags=re.IGNORECASE) can replace "A-Z"
				if (self.firstTurn):
					self.selectSquare(int(nums[1]))
				self.selectSquare(int(nums[2]))
			elif (line.startswith("Reset:")):
				self.reset(line[7:-1])
			elif (line.startswith("#") or (line == "\n")):
				pass #Comment or blank line
			elif (line.startswith("Version:")):
				pass #Not used yet
			elif (line.startswith("GameType:")):
				if (gameType == None):
					gameType=line[10:-1]
			elif (line.startswith("FinalScore:")):
				final = line[12:] #can be confirmed later
			elif (line.upper().startswith("END")):
				break
			else: 
				self.gameType = "FAIL"
				#self.__init__(self.table[0].get_parent(),self.status)
				raise Exception("Invalid Save Game File!\nUnknown Line("+str(index)+"): \""+line[:-1]+"\"")
		self.gameType = gameType
		self.AIMethod = Aikisolver.getMethod(gameType)
		if (self.AIMethod != None) and (self.turn == "White"):
			self.makeMove(self.AIMethod(self))
		
		if self.winner:
			self.reset()
	
	#Toggles whether or not dots that show possible moves should be displayed and adds/removes them accordingly.	
	def toggleShowMoves( self, movesOn ):
		global showMoves
		
		if (self.selectedPiece < 0):
			showMoves = movesOn
			return
			
		elif (not showMoves) and (movesOn):
			#Display the possible moves!
			showMoves = True
			self.markEligible()

		elif ((showMoves) and not (movesOn)):
			#Remove the possible moves marks from the board 
			showMoves = False
			for index, item in enumerate(self.eligible):
				if (item == "GOOD"):
					self.removePiece(index)
					if (self.turn == "Black") and (self.currentWhiteLayout[index] != "NULL"):
						#There was a Sumo Push available when toggled
						self.placePiece( index, self.currentWhiteLayout[index], "White" )
					elif (self.turn == "White") and (self.currentBlackLayout[index] != "NULL"):
						self.placePiece( index, self.currentBlackLayout[index], "Black" )
						
		#Else nothing really changed.
		
	#Determine the new cursor location based on input and draw it.
	def moveCursor(self, direction):
		limitCursorMovement = showMoves #True = Limit cursor movement to eligible moves
		cursorPos = self.cursorPos
		eligible = self.eligible[:]
		if (self.firstTurn):
			#This lets the cursor go over the pieces on the first turn
			if (self.turn == "Black"):
				for num in xrange(0,8):
					eligible[num] = "GOOD"
			else:
				for num in xrange(56,64):
					eligible[num] = "GOOD"
		#self.printBoard(eligible)
		
		#Determine the new cursor position
		if (limitCursorMovement == False):
			if (direction == gtk.keysyms.Up):
				cursorPos += 8
			elif (direction == gtk.keysyms.Down):
				cursorPos -= 8
			elif (direction == gtk.keysyms.Left):
				cursorPos += 1
			elif (direction == gtk.keysyms.Right):
				cursorPos -= 1
		else :
			try:
				if (direction == gtk.keysyms.Up):
					while True:
						cursorPos += 8
						if (cursorPos > 63):
							#Went past the Top edge; Attempt to go diagonal.
							cursorPos = self.cursorPos
							if (cursorPos + 8 < 64):
								if (cursorPos%8 > self.selectedPiece%8):
									if (eligible[cursorPos + 9] == "GOOD"):
										cursorPos += 9
									elif (eligible[cursorPos + 7] == "GOOD"):
										cursorPos += 7
								elif (eligible[cursorPos + 7] == "GOOD"):
									cursorPos += 7
								elif (eligible[cursorPos + 9] == "GOOD"):
									cursorPos += 9
							break
						if (eligible[cursorPos] == "GOOD"):
							break
				elif (direction == gtk.keysyms.Down):
					while True:
						cursorPos -= 8				
						if (cursorPos < 0):
							cursorPos = self.cursorPos
							if (cursorPos - 8 >= 0 ):
								if (cursorPos%8 < self.selectedPiece%8):
									if (eligible[cursorPos - 9] == "GOOD"):
										cursorPos -= 9
									elif (eligible[cursorPos - 7] == "GOOD"):
										cursorPos -= 7
								elif (eligible[cursorPos - 7] == "GOOD"):
									cursorPos -= 7
								elif (eligible[cursorPos - 9] == "GOOD"):
									cursorPos -= 9
							break
						if (eligible[cursorPos] == "GOOD"):
							break
				elif (direction == gtk.keysyms.Left):
					while True:
						cursorPos += 1
						if (cursorPos%8 == 0):
							#Went past the Left edge and looped around; Attempt to go diagonal.
							if (self.cursorPos%8 == 7):
								cursorPos = self.cursorPos
							elif (eligible[self.cursorPos + 9] == "GOOD"): #Try to go up #(self.cursorPos < 56) and
								cursorPos = self.cursorPos + 9
							elif (eligible[self.cursorPos - 7] == "GOOD"): #Try to go down
								cursorPos = self.cursorPos - 7
							else: #Can't go anywhere left
								cursorPos = self.cursorPos
							break
						if (eligible[cursorPos] == "GOOD"):
							break
				elif (direction == gtk.keysyms.Right):
					while True:
						cursorPos -= 1
						if (cursorPos%8 == 7):
							if (self.cursorPos%8 == 0):
								cursorPos = self.cursorPos
							elif (eligible[self.cursorPos + 7] == "GOOD"): #Try to go up #(self.cursorPos < 56) and
								cursorPos = self.cursorPos + 7
							elif (eligible[self.cursorPos - 9] == "GOOD"): #Try to go down
								cursorPos = self.cursorPos - 9
							else:
								cursorPos = self.cursorPos
							break
						if (eligible[cursorPos] == "GOOD"):
							break
			except Exception, e:
				#Tried to go off the board
				#if (debug): print "OB:",e
				cursorPos = self.cursorPos
		
		#Determine if new cursor position is valid
		if (cursorPos >= 0) and (cursorPos <= 63):
			bg = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/"+self.boardLayout[self.cursorPos]+"BG.png")
			self.table[self.cursorPos].get_child().set_from_pixbuf(bg)
			if (self.currentBlackLayout[self.cursorPos] != "NULL"):
				self.placePiece( self.cursorPos, self.currentBlackLayout[self.cursorPos], "Black" )
			elif (self.currentWhiteLayout[self.cursorPos] != "NULL"):
				self.placePiece( self.cursorPos, self.currentWhiteLayout[self.cursorPos], "White" )
			if (self.selectedPiece == self.cursorPos):
				self.markSelected()	
			elif (not self.firstTurn) or (self.cursorPos > 7) and (self.cursorPos < 56):
				self.markEligible(place=self.cursorPos)
			self.cursorPos = cursorPos
			#GET BG pixbuf
			bg = self.table[self.cursorPos].get_child().get_pixbuf()
			#Get Piece pixbuf
			cursor = gtk.gdk.pixbuf_new_from_file(pwd+"/GUI/TileSets/"+TileSet+"/CursorMark.png")
			cursor.composite(bg, 0, 0, tileSize, tileSize, 0, 0, 1, 1, gtk.gdk.INTERP_HYPER, 255)
			self.table[self.cursorPos].get_child().set_from_pixbuf(bg)
		#Else: it didn't move.

	
	def overlayBoard(self, array=None):
		"""Puts text over each square on the board; Useful for debugging."""
		#pixbuf = self.table[1].get_child().get_pixbuf()
		for index,square in enumerate(self.table):
			pixbuf = square.get_child().get_pixbuf()
			pixmap, mask = pixbuf.render_pixmap_and_mask()
			if (array==None):
				textLay = square.create_pango_layout(' '+str(index))
			else:
				textLay = square.create_pango_layout(array[index])
			#textLay = Widget.create_pango_layout('1')
			pixmap.draw_layout(pixmap.new_gc(), 0, 0, textLay, gtk.gdk.Color(255, 0, 0))
			#self.table[1].get_child().set_from_pixmap(bg,mask)
			pixmap = gtk.gdk.Pixbuf.get_from_drawable(pixbuf,pixmap,pixmap.get_colormap(),0,0,0,0,48,48)
			square.get_child().set_from_pixbuf(pixmap)

		#self.table[1].get_child().set_from_pixbuf(pixmap)		
	
	def printBoard(self, array):
		"""Prints an 8x8 array so that it's human readable; Useful for debugging."""
		print ""
		for index, item in enumerate(reversed(array)):
			print str(item+"           ")[:9],#12
			if (index%8 == 7):
				print ""
		print ""
		
		
#End of class: GameBoard

class Aikisolver:
	"""Library for determining the best moves"""
	#Returns the appropriate method so that we don't need to find the proper method each time
	@staticmethod
	def getMethod(difficulty):
		if (difficulty == "Local-AI-Easy"):
				return Aikisolver.easyAI
		elif (difficulty == "Local-AI-Medium"):
				return Aikisolver.mediumAI
		elif (difficulty == "Local-AI-Hard"):
				return Aikisolver.hardAI
		return None
		
	#Just selects the farthest possible move
	@staticmethod
	def tooEasyAI(gameBoard): 
		assert(gameBoard.turn == "White") #Computer should always be black... for now at least
		eligible = Aikisolver.generateEligible(gameBoard)
		for index, item in enumerate(eligible):
			if item == "GOOD":
				return index
		return 0

	#Finds the farthest move that wont cause the human to win
	@staticmethod	
	def easyAI(gameBoard):
		assert(gameBoard.turn == "White")
		eligible = Aikisolver.generateEligible(gameBoard)
		humanWins = {}
		
		for index, item in enumerate(eligible): #look at every possible move
			if (item == "GOOD"):
				if (index <= 7):
					#Found winning move
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
		"""Tries to threaten the home row and wont move to a place that will cause the opponent to win
			All possible moves are ranked by how good they seem and how good the humans next move could be.
			Among all moves with the same rank a modifier is applied to break the stalemate;
			upto 0.5 is added based on proximity to the oponents home and up to another 0.5 is added at random."""
		
		#Subroutine: takes in an "eligible" and spits out a "move" -> (priority, position)
		def heuristic():
			#TODO#generalize to allow computing black moves too
			assert(gameBoard.turn == "White")
			for index, item in enumerate(eligible): #Look at every possible AI move
				if (item == "GOOD"):
					if (index <= 7):
						#Found winning move
						return ('9',index)

					color = gameBoard.boardLayout[index] #Color of the board where were looking at moving the AI to
					humanPiece = gameBoard.currentBlackLayout.index(color) #The piece the human would move next if index was chosen by the AI
					tempEligible = Aikisolver.generateEligible(gameBoard, humanPiece, index)
					priority = 3+random.random() #Will remain 3 if this piece has no moves and will cause the players turn to be skipped
					#Look for human wins
					for tempIndex, tempItem in enumerate(tempEligible): #For every possible move of the human piece
						if (tempItem == "GOOD"):
							if (tempIndex >= 56):
								if gameBoard.currentSumoLayout[humanPiece] == "NULL":
									priority = 0+random.random()#The human will win if the AI lands on this color
								else:
									priority = -1+random.random() #The human's Sumo will win...
								break
							priority = 1 #Will remain 1 if this piece will be locked down (no moves) by moving there
			
					#if (priority = 3): Make sure moving to a color for which the human has no moves (and skipping their turn) will be worth it.
					#if (priority = 1): Check for any moves that would threaten their home row
					if (not int(priority) == 0): #Position has possible moves
						tempEligible = Aikisolver.generateEligible(gameBoard, index, tempMissing=humanPiece)
						modifier = float(6-index/8)/10 #The farther the piece gets, the higher the liklihood it will be chosen
						#Find out how good this move is
						for tempIndex, tempItem in enumerate(tempEligible):
							if (tempItem == "GOOD"):
								if (int(priority) == 1):
									modifier += random.random()/2 #Adds a random element
									assert(modifier < 1) #If the modifier reaches 1 it can push the priority up
									priority = 2+modifier #Position has possible moves, but there not necessarily good.
								if (tempIndex <= 7):	
									priority += 2 #Threatens the home row
									break
					
						#TODO#test this! maybe it does not work, maybe the priority need to be lowered even more.
						#Avoid moving in front of a sumo	
						if (not gameBoard.currentSumoLayout[index-8] == "NULL") and (priority < 5):
							tempEligible = Aikisolver.generateEligible(gameBoard, index-8)
							if (tempEligible[index] == "GOOD"):
								#print "Avoiding Sumo @ ",index-8,"!"
								priority -= 1
			
					eligible[index] = "Prio="+str(priority) #Priority
			
			if (debug):
				#gameBoard.overlayBoard(eligible)
				#gameBoard.overlayBoard()
				gameBoard.printBoard(eligible)
				#processAllGtkEvents()
				#time.sleep(5)
				#md = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO, buttons= gtk.BUTTONS_OK, message_format='Click "OK" to continue.')
				#md.run()
				#md.destroy()
			
			#Find the best move
			bestMove = (-2, -2)
			for index, item in enumerate(eligible):				
				if (item[:4] == "Prio"):
					if (item[5:] > bestMove[0]):
						bestMove = (item[5:], index)
			
			return bestMove
		#END: heuristic():
		
		#mediumAI: Main Logic
		eligible = Aikisolver.generateEligible(gameBoard)
		checkSumo = (not gameBoard.currentBlackLayout[gameBoard.selectedPiece-8] == "NULL") and (eligible[gameBoard.selectedPiece-8] == "GOOD")
		move = heuristic()

		sumoMove = (-1,-1)
		if (checkSumo):
			pushType = gameBoard.currentSumoLayout[gameBoard.selectedPiece]
			#Evaluate the value of the next move
			#print "contemplating Sumo Push..."
			#print "if sumo, next move would be: ",gameBoard.boardLayout[gameBoard.selectedPiece-16]
			if (gameBoard.selectedPiece-24 >= 0) and (not gameBoard.currentBlackLayout[gameBoard.selectedPiece-24] == "NULL"): #Double Push
				eligible = Aikisolver.generateEligible(gameBoard, gameBoard.currentWhiteLayout.index(gameBoard.boardLayout[gameBoard.selectedPiece-24]))
			else:
				eligible = Aikisolver.generateEligible(gameBoard, gameBoard.currentWhiteLayout.index(gameBoard.boardLayout[gameBoard.selectedPiece-16]))
			#print "CBL:",gameBoard.currentBlackLayout
			#print "eligible:",eligible
			sumoMove = heuristic()
			#print "SumoPush: ",sumoMove
		#print "Move: ",move
		
		if (sumoMove[0] >= move[0]):
			return gameBoard.selectedPiece-8 #Because the sumo move contains the location of the next move
		return move[1]

	#A* search using the heuristic: (number of colors in which the AI threatens) - (the number of color that the human threatens)
	@staticmethod
	def hardAI(gameBoard):
		#TODO#Implement everything!
		print "HardAI: not yet implemented"
		return Aikisolver.mediumAI(gameBoard)
		#whats to come:
		#helper functions:
		def replicateMoves(path): #FIXME#don't know if this works
			#Will mutate tempBoard so that it can be evaluated by generate eligible
			splitPath = path.split(',')
			for item in splitPath:
				print "item: ",item
				tempBoard.selectSquare(item)
		
		#TODO#rates the move based on...
		#Subroutine: 
		def heuristic():
			return 0
		
		class node:
			def __init__(self, value, path, humanMove):
				self.value = value
				self.path = path
				self.humanMove = humanMove
				self.children = []
			
		#Main part of hardAI
		tempBoard = copy.copy(gameBoard)
		heap = Queue.PriorityQueue() #lowest score first -> tuple(score, node)
		root = node(0, "", False)
		heap.put((root.value,root))
		#for i in xrange(100):
		while (not heap.empty()):
			parentNode = heap.get()[1]
			tempBoard = copy.copy(gameBoard)
			replicateMoves(parentNode.path)
			Aikisolver.generateEligible(tempBoard)
			parentNode.value = hurestic()
			##TODO## where i last left off.
		
		return Aikisolver.mediumAI(gameBoard)

	#Find all possible moves for one piece
	@staticmethod
	def generateEligible(gameBoard, tempSelected = "NULL", tempBlocker = "NULL", tempMissing=None):
		#tempSelected, tempDestination, and tempMissing are used to simulate a possible move
		if (tempSelected == "NULL"):
			num = gameBoard.selectedPiece
		else :
			num = tempSelected
		if (not gameBoard.currentBlackLayout[num] == "NULL"):
			turn = "Black"
		else :
			turn = "White"

		#Inserting Colored pieces into the list
		eligible = gameBoard.sumoPieceLayout[:]
		for index, item in enumerate(gameBoard.currentBlackLayout):
			if (index != tempMissing):
				eligible[index] = item
		for index, item in enumerate(gameBoard.currentWhiteLayout):	
			if (item != "NULL"):
				eligible[index] = item
		
		if (not tempBlocker == "NULL"):
			#AI: places a temp piece to simulate the intended move blocking the humans advances
			eligible[tempBlocker] = "TEMP"
		
		eligible[gameBoard.selectedPiece] = "NULL" #AI: makes sure that the place a piece moved out of is considered
		eligible[num] = "GOOD"
		
		#Unprofessionally determines which positions are valid.
		#TODO#Some of the Black and White specific code could be aggregated by multiplying the indices by '-1' and using a dict for the currentLayouts
		if (turn == "Black"):
			#looks for viable moves above num
			i = 0
			#This algorithm relies on the fact that every 7th space from the origin is on the diagonal, etc.
			#num%8 is the position along the row(0-7). it can iterate this may times before it hits a wall
			#7-num/8 is the number of times it can iterate before hitting the ceiling
			while (i < num%8) and (i < 7-num/8) and (eligible[i*7+num] == "GOOD"): 	
				i = i + 1
				#Checks every 7th to make sure its not occupied.
				if (eligible[i*7+num] == "NULL"):
					if (gameBoard.currentSumoLayout[num] == "NULL") or ((gameBoard.currentSumoLayout[num] == "Black") and (i <= 5)) or ((gameBoard.currentSumoLayout[num] == "SuperBlack") and (i <= 3)):
						#Not a sumo or is but within distance limit
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
			
			#Looks for a Sumo Push - if the selected piece is a sumo and has a non sumo enemy piece directly in front with space to push. 
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
			#Looks for viable moves below num
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

			#Looks for a Sumo Push
			if (gameBoard.currentSumoLayout[num] != "NULL") and (num >= 16):
				#Single Sumo Push
				if (gameBoard.currentBlackLayout[num-8] != "NULL") and ((gameBoard.currentSumoLayout[num-8] == "NULL") or (gameBoard.currentSumoLayout[num] == "SuperWhite")) and (eligible[num-16] == "NULL"):
					eligible[num-8] = "GOOD"
			
				elif (gameBoard.currentSumoLayout[num] == "SuperWhite") and (num >= 24):
					#Double Sumo Push
					if (gameBoard.currentBlackLayout[num-8] != "NULL") and (gameBoard.currentBlackLayout[num-16] != "NULL") and (gameBoard.currentSumoLayout[num-8] != "SuperBlack") and (gameBoard.currentSumoLayout[num-16] != "SuperBlack") and (eligible[num-24] == "NULL"):
						eligible[num-8] = "GOOD"
		
		#So that the selected piece is not marked.
		eligible[num] = "BAD"

		return eligible
		
#End of class Aikisolver

#Used to create and handle server/game connections
class NetworkConnection():
	import socket
	#The state of this "connection" is held by self.connectionStatus. possible values include:
	#Server - connected to the lobby server and browsing opponents
	#awaiting response - a challenge has been issued
	#awaiting challenge - the seek loop is running
	#challenge received - the user has been challenged 
	#game 
	#dead

	#Makes contact with the lobby server @serverAddress
	def __init__( self, cbw ):
		print "Trying to contact game server at ", serverAddress
		self.callBackWidget = cbw
		self.challengeTimeout = 15
		self.connectionStatus = "Bad"
		self.callback = False
		self.killSeekLoop = True
		self.killChallengeLoop = True
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
			print "Server not found"			

	#Platform-Specific way to notify the GUI of events
	def callBackActivate(self):
		self.callback = True
		self.callBackWidget.activate()
	
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
				#Set client's name
				self.name = name
				##self.challengeLock = threading.Lock()
				##self.challengeLock.acquire()
				self.servSock = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
				self.servSock.bind(('', gamePort))
				self.servSock.listen(1)
				self.servSock.settimeout(3)
				self.lobbySock.send("name="+name)
				print "threading seek process..."
				self.threadSeekLoop()
				return True
			else :
				print "already seeking"
				return False
		except self.socket.error :
			print "Failed, Socket Still in use!"
			return False
		except :
			print "oops! seek init failed..."
			return False

	#Threads a "Server Loop" that waits for a game connection then notifies the main GUI
	def threadSeekLoop(self):
		#Subroutine to be threaded
		def seekLoop():
			#Waiting for remote user to issue challenge
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
					#Accept timed out
					pass
				
			print "seek ended."
			self.killSeekLoop = True
		#END: seekLoop()
		threading.Thread(target=seekLoop, args=()).start()

	#Kills the seek loop and sets the status to "Server"
	def cancelSeekLoop(self):
		print "Canceling seek..."
		self.lobbySock.send("cancel=") # removes the name from the list
		self.connectionStatus = "Server"
		self.killSeekLoop = True

	#Issue challenge and start a thread to wait for the potential opponent to respond to your challenge
	def challenge(self, ip):
		#Subroutine: Waits for a challenge Response
		def challengeLoop(ip, stub):
			try :
				self.gameSock = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
				self.gameSock.settimeout(1)
				self.gameSock.connect((ip , gamePort))
				self.killChallengeLoop = False
				i = 0
				string = ""
				while (not self.killChallengeLoop) and (string == ""):
					print "loop: ",i
					i=i+1
					if (i > self.challengeTimeout): raise Exception("Ignored")
					try:
						string = self.gameSock.recv(1024)
					except:
						pass 
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
					print "failed to close gamesock after crash/timeout in NetworkConnection.challenge.challengeLoop()"
				self.connectionStatus = "Server"
				print "challenge ignored."
			
			self.callBackActivate()
		#END: challengeThread()
		
		self.killSeekLoop = True
		print "issued challenge to IP: ", ip
		self.connectionStatus = "issuing challenge"
		threading.Thread(target=challengeLoop, args=(ip, "stub")).start()
		
	#Reply to the remote user who challenged you
	def answerChallenge(self, accept, localColor):
		if (accept):
			print "challenge accepted!"
			if (self.connectionStatus == "challenge received"):
				self.gameSock.send("challenge accepted")
			self.connectionStatus = "Game"
			self.disconnectServer()
			self.gameSock.settimeout(3)
			if (localColor == "White"):
				self.threadMoveLoop()
			##self.challengeLock.release()
		else :
			#Challenge declined... seek must be restarted
			print "challenge declined."
			self.gameSock.send("challenge declined")
			self.gameSock.shutdown(self.socket.SHUT_RDWR) 
			self.gameSock.close()
			self.threadSeekLoop()
	
	#Used by the GUI to tell why it was just called 
	def status( self ):
		return self.connectionStatus

	#Makes a thread that waits for the the opponent to sent their move
	def threadMoveLoop(self):
		#Subroutine: waits until the move is received.
		def moveLoop():
			#print "starting move loop..."
			self.killMoveLoop = False
			i = 0
			while (not self.killMoveLoop):
				try :
					string = self.gameSock.recv(1024)
					print "received: ", string
					if (string[:4] == "Move"):
						#print "string= ",string
						if (string[-5:] == "Turn!"):
							print "received two commands!"
							self.recentMove = string[5:-5]
							self.callBackActivate()
							break
						self.recentMove = string[5:]
						#print "recentMove= ",self.recentMove
						self.callBackActivate()
					elif (string[:4] == "Turn"):
						#print "Its the local players turn."
						break
					elif (string[:4] == "Refo"):
						self.connectionStatus = string
						self.callBackActivate()
						break
					else : 
						print "something got messed up while waiting for the remote move..."
						self.disconnectGame()
						self.callBackActivate()
						break
					
				except self.socket.timeout: 
					#Timeouts are perfectly normal, it means the connection is a live but not sending
					print "Still waiting for the remote move..."
				except : 
					#print "Non-fatal Network Error..."
					if (i >= 10):
						#This many errors means the connection was closed. one or two errors can happen
						print "Remote Game Connection Lost."
						self.disconnectGame()
						self.callBackActivate()
					else :
						i = i +1

			#print "move loop ended..."
		#END: moveLoop()
		threading.Thread(target=moveLoop, args=()).start()

	#Used by the GUI to find out what the remote players move was
	def getMove(self):
		try:
			return int(self.recentMove)
		except:
			print "move not an int: ",self.recentMove
			self.disconnectGame()
		
	#Tells the opponent what you move was		
	def sendMove( self, pos, turnOver ):
		try:
			print "Sending Move: ", pos
			self.gameSock.send("Move="+str(pos))
			if (turnOver):
				#Let the remote player know its their turn
				self.gameSock.send("Turn!")
				#Wait for response
				self.threadMoveLoop()
		except :
			#TODO#recover gracefully
			print "Fatal Network Error!"
	
	#Tells the opponent how to reform the board for the next match		
	def reform( self, reformType ):
		self.gameSock.send("Reform="+reformType)
		self.threadMoveLoop()
	
	def disconnectServer(self): #Used to properly disconnect from the lobby
		if (self.killSeekLoop == False):
			self.cancelSeekLoop()
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
	
#End of class: 	NetworkConnection

#Used to define all of the functions the GUI needs.
class GameGui:
	#Loads the GUI file, connects signals, etc.
	def __init__( self ):
		#Loads the GUI file
		self.builder = gtk.Builder()
		self.builder.add_from_file(pwd+"/GUI/main.ui")
		self.localColor = "Null"
		self.connection = 0
		self.startNewGame()
		self.fullscreen = False
		self.gameWindowEscape = True
		self.konami = 0
		
		#Add File Filters to the openFileChooser
		self.builder.get_object("aikFileFilter").set_name("Aikisado Saved Games (*.aik)")
		self.builder.get_object("aikFileFilter").add_pattern("*.[Aa][Ii][Kk]")
		self.builder.get_object("allFileFilter").set_name("All Files")
		self.builder.get_object("allFileFilter").add_pattern("*")
		self.builder.get_object("openFileWidget").add_filter(self.builder.get_object("aikFileFilter"))
		self.builder.get_object("openFileWidget").add_filter(self.builder.get_object("allFileFilter"))
		
		#Find and list tilesets.
		self.tileSetList = os.listdir(pwd+"/GUI/TileSets")
		self.tileSetMenu = list()
		for item in self.tileSetList:
			tmp = gtk.RadioMenuItem( self.tileSetMenu[0] if self.tileSetMenu else None,item)
			self.tileSetMenu.append(tmp)
			self.builder.get_object("tileSetMenu").append(tmp)
			tmp.connect("activate", self.selectTileSet)
			tmp.show()
			if (item == "Original"):
				tmp.activate()
		
		#And add the info Info Bar for GTK version 2.22+
		try:
			self.infobar = gtk.InfoBar()
			self.infobar.set_message_type(gtk.MESSAGE_ERROR)
			label = gtk.Label()
			label.set_markup('<span foreground="black">Error Loading File! Please choose another.</span>');
			content = self.infobar.get_content_area()
			content.add(label)
			label.show()
			self.builder.get_object("openFileChooserVBox").pack_start(self.infobar,False,False)
			self.builder.get_object("openFileChooserVBox").reorder_child(self.infobar,0)
		except:
			self.infobar = None
		
		#Format the tree View
		seekTreeView = self.builder.get_object("seekTreeView")
		cellRend = gtk.CellRendererText()
		nameColl = gtk.TreeViewColumn("Name", cellRend, text=0)
		ipColl = gtk.TreeViewColumn("IP", cellRend, text=1)
		seekTreeView.append_column(nameColl)
		seekTreeView.append_column(ipColl)
		self.seekStore = gtk.ListStore(str, str)
		seekTreeView.set_model(self.seekStore)
		seekTreeView.set_reorderable(True)
		
		#Initalize Menu options
		self.builder.get_object("showMovesBox").set_active(showMoves)
		self.builder.get_object("enableAnimationsBox").set_active(enableAnimations)
		
		#The menu cant be placed correctly the first time becasue it has no height until it is poped up once
		self.builder.get_object("prefsMenu").popup(None, None, None, 1, 0)
		self.builder.get_object("prefsMenu").popdown()
		
		#Outlines each event and associates it with a local function
		dic = { 
			#Global Events
			"gtk_widget_hide" : self.widgetHide,
			"on_callBack_activate" : self.callBack,
			"on_gameWindow_key_press_event" : self.keyPress,
			"on_gameWindow_key_release_event" : self.keyPress,
			
			#Main Window
			"on_gameWindow_destroy" : self.quit,
			"on_gameWindow_state_event" : self.toggleFullscreen,
			"tile_press_event" : self.tilePressed,
			"on_sendButton_clicked" : self.sendChat,
			"on_testingButton_clicked" : self.test,

			#Toolbar
			"on_newGameToolButton_clicked" : self.newGameDialog,
			"on_undoToolButton_clicked" : self.undo,
			"on_saveToolButton_clicked" : self.save,
			"on_prefsToolButton_toggled" : self.prefsOpen,
			"on_helpToolButton_clicked" : self.help,
			"on_aboutToolButton_clicked" : self.about,
			
			#Prefs Menu
			"on_prefsMenu_deactivate" : self.prefsClose,
			"on_enableAnimationsBox_toggled" : self.toggleAnimations,
			"on_showMovesBox_toggled" : self.toggleMoves,

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

			#openFileChooser
			"on_openFileChooser_response" : self.load,
			
			#saveFileChooser
			"on_saveFileChooser_response" : self.save,
			
			#confirmExitDialog
			"on_exitCancelButton_clicked" : self.confirmExit,
			
			#Update Dialog
			"on_updateYesButton_clicked" : self.updateDialog,
			"on_updateNoButton_clicked" : self.updateDialog
			
		}
		blah = self.builder.connect_signals( dic )

	#Used to test features and subroutines because it can be easily connected to a button and tried.
	def test(self, widget=None, event=None):
		print "TEST:"
		self.stub(widget,event)
		print "debug:",debug
		
	#Temporarily connected to GUI elements that have not been implemented but are there for aesthetics.
	def stub(self, widget, event = 0):
		print "STUB:"
		print "widget: ", widget
		print "event: ", event
		print "Feature not yet implemented."

	#For intercepting the "delete-event" and instead hiding
	def widgetHide(self, widget, trigeringEvent):
		#print widget,trigeringEvent
		#print "HIDE!"
		self.gameWindowEscape = False
		if (widget == self.builder.get_object("waitingDialog")):	 
			self.closeWaitingDialog()
		elif (widget == self.builder.get_object("lobbyDialog")):
			self.lobbyCancel()
		widget.hide()
		return True

	#Gracefully shut everything down
	def quit(self, widget=None):
		#print "Exiting Aikisado."
		self.killProgressBar = True
		try:
			self.connection.disconnectServer()
		finally :	
			try :
				self.connection.disconnectGame()
			finally :
				sys.exit(0)

	#Passes info to GameBoard and checks for a winner
	def tilePressed(self, widget=None, trigeringEvent=None, pos=None):
		#print "Pressed Button: ", widget.get_child().get_name()
		#print widget,trigeringEvent,pos
		if (pos == None):
			if (trigeringEvent.button == 1):
				#print widget.get_name()
				if (widget.get_name()=="GtkEventBox"):
					#Only the event boxes handle Left-Clicks.
					#Normal Left-click; activates area under the mouse cursor
					pos = widget.get_child().get_name()
				else: 
					return
			else:
				#Right-click or Middle-click; activates area under the keyboard cursor; same as enter
				pos = self.board.cursorPos

		#Pass the board the gameTable so it can mess with the images.
		if not (self.board.winner): 
			if (self.board.gameType[:5] == "Local") or (self.board.turn == self.localColor):
				turnOver = self.board.selectSquare(int(pos))
				#turnOver is true if the players turn is over.
				if (self.board.gameType == "Network"):
					self.connection.sendMove(int(pos), (turnOver and (not self.board.winner)))
				if (turnOver):
					if (self.board.gameType == "Network"):
						self.builder.get_object("statusLabel").set_text("It's the Remote Players turn...")
					else :
						self.builder.get_object("undoToolButton").set_sensitive(True)
					if (self.board.gameType.startswith("Local-AI")) and (not self.board.winner):
						self.builder.get_object("statusLabel").set_text("It's Your Turn! ("+self.board.turn+")")
					
					self.builder.get_object("saveToolButton").set_sensitive(True)
						
			#Else : wait for remote player to select a piece	

		if (self.board.winner == True): 
			self.announceWinner()

	#Congratulate the winner (and ask for reform type) or shame the looser.
	def announceWinner(self):
		self.builder.get_object("undoToolButton").set_sensitive(False)
		if ((self.board.gameType == "Network") and (self.board.turn != self.localColor)) or ((self.board.gameType.startswith("Local-AI")) and (self.board.turn == "White")):
			#the remote/AI player won
			pos = self.builder.get_object("gameWindow").get_position()
			self.builder.get_object("sorryDialog").move(pos[0]+93, pos[1]+75)
			self.builder.get_object("sorryDialog").present()
		
		else :
			#A local player won
			#print "color: "+self.board.turn+", type: "+self.board.gameType
			self.builder.get_object("gratsLabel").set_text(self.board.turn+" Wins!!")#("Congratulations "+self.board.turn+",\n        You Win!!")
			pos = self.builder.get_object("gameWindow").get_position()
			self.builder.get_object("gratsDialog").move(pos[0]-13, pos[1]+75)
			self.builder.get_object("gratsDialog").present()

		self.builder.get_object("scoreLabel").set_text("Black: "+str(self.board.blackWins)+" | White: "+str(self.board.whiteWins))

	#Tells the GameBoard to toggle whether or not the possible moves should be shown
	def toggleMoves(self, widget):
		self.board.toggleShowMoves(self.builder.get_object("showMovesBox").get_active())
		writeConfigItem("ShowMoves",showMoves)

	#Ask the user what type of game they want to start
	def newGameDialog(self, widget="NULL"):
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("newGameDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("newGameDialog").present()

	#Self explanatory
	def newGameDialogHide(self, widget, event=None):
		self.builder.get_object("newGameDialog").hide()

	#Kicks off a new local game ,opens a save-file or starts a connection with the lobby server to find an online opponent
	def startNewGame(self, widget="NULL"): 
		
		if (not self.connection == 0):
			#Close the current game or server connection
			print "Closing game connection with other player!"
			self.connection.disconnectServer()
			self.connection.disconnectGame()
			self.connection = 0
		if (self.builder.get_object("networkGameRadioButton").get_active()):
			#Starting a new network Game (starting to find)
			#Hand the NetworkConnection class a way to callback.
			if (platform.system() == "Windows"): #FIXME#these should use "callBackWidget"
				self.connection = NetworkConnection(self.builder.get_object("lobbyRefreshButton"))
			else:		
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
				
			else: #Unable to reach server
				#self.builder.get_object("noServerWarningDialog").set_message("The server at \""+serverAddress+"\" was not found!")
				pos = self.builder.get_object("gameWindow").get_position()
				self.builder.get_object("noServerWarningDialog").move(pos[0]+25, pos[1]+75)
				self.builder.get_object("noServerWarningDialog").present()
		
		elif (self.builder.get_object("openFileRadioButton").get_active()):
			#Open a previously saved file to be parsed and displayed.
			self.builder.get_object("openFileWidget").set_current_folder(savePath)
			self.load()
			self.newGameDialogHide( self )
			
		else:
			#User selected an AI game
			#Passing the method directly prevents having to check difficulty again later
			if (self.builder.get_object("EasyAIRadioButton").get_active()):
				gameType = "Local-AI-Easy"
			elif (self.builder.get_object("MediumAIRadioButton").get_active()):
				gameType = "Local-AI-Medium"
			elif (self.builder.get_object("HardAIRadioButton").get_active()):
				gameType = "Local-AI-Hard"
			else :
				#Starts a new local game
				gameType = "Local"
						
			self.board = GameBoard(self.builder.get_object("gameTable"), self.builder.get_object("statusLabel"), gameType)
			self.newGameDialogHide( self )
			if (self.board.gameType.startswith("Local-AI")):
				self.builder.get_object("statusLabel").set_text("It's Your Turn! ("+self.board.turn+")")
			self.builder.get_object("scoreLabel").set_text("Black: 0 | White: 0")
	
		#Hide chatFrame
		self.builder.get_object("chatFrame").hide()
		self.builder.get_object("undoToolButton").set_sensitive(False)
		self.builder.get_object("saveToolButton").set_sensitive(False)

	#Pull a new list from the lobby server.
	def lobbyRefresh(self, widget="NULL"):
		#this button doubles as a call back for self.connection
		if (self.connection.callback == True):
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

	#Makes the top opponent in the lobby list the focus/default so it is activated when the user presses enter		
	def treeViewFocus(self, wigdet, event):
		self.builder.get_object("lobbyChallengeButton").grab_focus()

	#Makes the seek button the focus/default so it is activated when the user presses enter
	def seekButtonFocus(self, wigdet, event):
		self.builder.get_object("lobbySeekButton").grab_default()

	#Kill the lobby connection and hide the dialog 
	def lobbyCancel(self, widget=None):
		self.connection.disconnectServer()
		self.builder.get_object("lobbyDialog").hide()
		self.builder.get_object("hostName").set_sensitive(True)
		self.builder.get_object("lobbySeekButton").show()
		self.builder.get_object("lobbyStopButton").hide()
		self.newGameDialog()
		
	#Tells the NetworkConnection class to start waiting for an opponent
	def seekNetworkGame(self, widget):
		print "Status: "+self.connection.status()
		print "Clicked Seek."
		string = self.builder.get_object("hostName").get_text()
		
		if (string != "") and (self.connection.status() == "Server"): #not seeking...
			pos = self.builder.get_object("gameWindow").get_position()
			self.builder.get_object("challengeDialog").move(pos[0]+25, pos[1]+75)
			try :
				worked = self.connection.seekOpponent(string)
			except Exception as error:
				print "ERROR:(seekNetworkGame)\n",error
				#Ends a currently running game
				self.connection.disconnectGame()
				self.connection.seekOpponent(string)
			
			if (worked):
				self.builder.get_object("hostName").set_sensitive(False)
				self.builder.get_object("lobbySeekButton").hide()
				self.builder.get_object("lobbyStopButton").show()
				self.builder.get_object("lobbyStopButton").set_active(True)
				#TODO#Find out if it should focus the challenge button; some user might not want it to.
				self.builder.get_object("lobbyChallengeButton").grab_focus()
				
		elif (string != ""): #already seeking...
			self.builder.get_object("hostName").set_sensitive(True)
			self.builder.get_object("lobbySeekButton").show()
			self.builder.get_object("lobbyStopButton").hide()
			self.builder.get_object("lobbyChallengeButton").grab_focus()
			self.connection.cancelSeekLoop()
		
		self.lobbyRefresh()

	#Tells the NetworkConnection class to issue a challenge to the specified IP
	def issueChallenge(self, widget):
		(model, iter) = self.builder.get_object("seekTreeView").get_selection().get_selected()
		#name = self.seekStore.get_value(iter, 0)
		ip = self.seekStore.get_value(iter, 1)
		if (ip != self.connection.localIP): #makes sure your not trying to challenge yourself
			pos = self.builder.get_object("gameWindow").get_position()
			self.builder.get_object("waitingDialog").move(pos[0]+25, pos[1]+75)
			self.builder.get_object("waitingDialog").present()
			self.threadProgressLoop(self.builder.get_object("waitingProgressBar"),self.connection.challengeTimeout)
			#this cancels the seek, the button should be re-enabled
			self.builder.get_object("hostName").set_sensitive(True)
			self.builder.get_object("lobbySeekButton").show()
			self.builder.get_object("lobbyStopButton").hide()
			self.connection.challenge(ip)

	#Stops the progressLoop Thread and hides the dialog	
	def closeWaitingDialog(self, widget=None, event=None):
		self.connection.killChallengeLoop = True
		self.killProgressBar = True
		self.builder.get_object("waitingDialog").hide()

	#Used by various threads to start a GUI event
	def callBack(self, widget=None):
		#print "Called Back: "+self.connection.status()
		self.connection.callBack = False
		if (self.connection.status() == "challenge received"):
			#Challenge received from a remote player
			self.recieveChallenge()
		elif (self.connection.status() == "challenge accepted"):
			#The remote player accepted the locally issued challenge
			self.closeWaitingDialog(self)
			self.localColor = "White" #this ensures that the player who is challenged goes first
			self.startNetworkGame()
		elif (self.connection.status() == "Server"):
			if (not self.killProgressBar):
				#Challenge Refused
				#TODO#prevent starting a network game if the player you challenged accepts after you stop waiting.
				self.closeWaitingDialog(self)
				#self.builder.get_object("sorryLabel").set_text("Your challenge was refused.")
				#self.builder.get_object("sorryDialog").present()
			#else : you already stopped waiting.	
		elif (self.connection.status() == "Game"):
			#Moves a piece for the remote player
			switchTurns = self.board.selectSquare(self.connection.getMove())
			if (switchTurns): 
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

	#Lets the user know they were challenged and ask them if they want to proceed
	def recieveChallenge(self):
		#Displays the challenge dialog
		print "Challenge Received!"
		self.localColor = "Black" #this ensures that the player who is challenged goes first
		opponentIP = self.connection.address[0]
		self.builder.get_object("challengeLabel").set_text("You have been challenged by a player at: "+ opponentIP +" !")
		#TODO#The following lines don't work on older version of gtk. the work around is in "seekNetworkGame()"
		#pos = self.builder.get_object("gameWindow").get_position()
		#self.builder.get_object("challengeDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("challengeDialog").present()
		self.threadProgressLoop(self.builder.get_object("challengeProgressBar"),self.connection.challengeTimeout, self.builder.get_object("noChallengeButton"))#self.declineChallenge)

	#Tell the NetworkConnection to decline the challenge and hide the dialog
	def declineChallenge(self, widget="NULL"):
		print "declined Challenge!"
		#TODO# implement fail-safe
		#worked = self.connection.answerChallenge(False, "Null")
		self.builder.get_object("challengeDialog").hide()
		print "almost..."
		self.connection.answerChallenge(False, "Null")
		print "fin"

	#Initialize the proper values for starting a network game
	def startNetworkGame(self, widget="Null"): #called when a local/remote user accepts a challenge
		self.connection.answerChallenge(True, self.localColor)
		self.builder.get_object("hostName").set_sensitive(True)
		self.builder.get_object("lobbySeekButton").show()
		self.builder.get_object("lobbyStopButton").hide()
		print "Your Color: "+self.localColor
		self.builder.get_object("challengeDialog").hide()
		self.builder.get_object("lobbyDialog").hide()
		self.board = GameBoard(self.builder.get_object("gameTable"), self.builder.get_object("statusLabel"),"Network")
		self.builder.get_object("scoreLabel").set_text("Black: 0 | White: 0")
		#TODO#show chatFrame
		#self.builder.get_object("chatFrame").show()
		if (self.board.turn == self.localColor):
			self.builder.get_object("statusLabel").set_text("It's Your Turn! ("+self.board.turn+")")
		else :
			self.builder.get_object("statusLabel").set_text("It's the Remote Players turn...")
	#Tells the GameBoard to revert to the previous State
	def undo(self, widget):
		self.builder.get_object("undoToolButton").set_sensitive(False)
		self.board.undo()
		if (self.board.firstTurn):
			self.builder.get_object("saveToolButton").set_sensitive(False)
	
	#Asks the user where to save the save-file
	def save(self, widget, event = "NULL"):	
		self.ghettoSave(widget)
		return #TODO#make the GLADE saveFileChooser show a "confirm overwrite" dialog
		print "event: ",event
		print int(gtk.RESPONSE_OK)
		if (widget == self.builder.get_object("saveToolButton")):
			#Show save dialog
			filename = self.builder.get_object("saveFileChooser").get_filename()
			if (not filename):
				filename = ".aik"
			elif (not self.builder.get_object("saveFileChooser").get_filename().endswith(".aik")):
				filename = os.path.basename(self.builder.get_object("saveFileChooser").get_filename())+".aik"
			else :
				filename = os.path.basename(self.builder.get_object("saveFileChooser").get_filename())
			self.builder.get_object("saveFileChooser").set_current_name(filename)
			pos = self.builder.get_object("gameWindow").get_position()
			self.builder.get_object("saveFileChooser").move(pos[0]-25, pos[1]+75)
			self.builder.get_object("saveFileChooser").set_do_overwrite_confirmation(True)
			self.builder.get_object("saveFileChooser").present()
			print "Moves: ",self.board.moves
			return
		
		elif (event == 1):
			#Save file
			filename = self.builder.get_object("saveFileChooser").get_filename()
			if (not filename.endswith(".aik")):
				filename = filename+".aik"
			print "Saving moves to file: ",filename
			f = open(filename, 'w')
			f.write("Version: "+version+"\n")
			f.write("GameType: "+self.board.gameType+"\n")
			f.write("FinalScore: "+self.builder.get_object("scoreLabel").get_text()+"\n")
			for move in self.board.moves:
				f.write(move+"\n")	
			f.close()
			writeConfigItem("SavePath",os.path.dirname(filename))

		self.builder.get_object("saveFileChooser").hide()

	#FIXME#Temporarily replaces self.save
	#Asks the user where to save the save-file
	def ghettoSave(self, widget):
		chooser = gtk.FileChooserDialog(title="Save Game",action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		chooser.set_current_name(".aik")
		chooser.set_do_overwrite_confirmation(True)
		chooser.set_current_folder(savePath)
		response = chooser.run()
		filename = chooser.get_filename()
		chooser.destroy()
		if (response == gtk.RESPONSE_OK):
			if (not filename.endswith(".aik")):
				filename = filename+".aik"
			print "Saving moves to file: ",filename
			f = open(filename, 'w')
			f.write("Version: "+version+"\n")
			f.write("GameType: "+self.board.gameType+"\n")
			f.write("FinalScore: "+self.builder.get_object("scoreLabel").get_text()+"\n")
			for move in self.board.moves:
				f.write(move+"\n")
			f.close()
			writeConfigItem("SavePath",os.path.dirname(filename))
			
			if (widget == self.builder.get_object("saveExitButton")):
				#If the saveDialog was opened from the confirmExit dialog, Aikisado should quit.
				self.quit()
	
	#Open a previously saved file to be parsed and displayed.
	def load(self, widget=None, event=None):
		if (widget == None):
			if (self.infobar != None):
				self.infobar.hide()
			self.builder.get_object("openNormalRadioButton").set_active(True)
			self.builder.get_object("openFileChooser").present()
		elif (widget == self.builder.get_object("openFileButton")):
			global enableAnimations
			ea = enableAnimations
			self.builder.get_object("openFileChooser").hide()
			try:
				if (self.builder.get_object("openAnimateButton").get_active()):
					enableAnimations = True
				else:
					enableAnimations = False
				filename = self.builder.get_object("openFileWidget").get_filename()
				if self.builder.get_object("openNormalRadioButton").get_active():
					gameType = None
				elif self.builder.get_object("openLocalRadioButton").get_active():
					gameType = "Local"
				elif self.builder.get_object("openEasyAIRadioButton").get_active():
					gameType = "Local-AI-Easy"
				elif self.builder.get_object("openMediumAIRadioButton").get_active():
					gameType = "Local-AI-Medium"
				elif self.builder.get_object("openHardAIRadioButton").get_active():
					gameType = "Local-AI-Hard"
				self.board = GameBoard(self.builder.get_object("gameTable"), self.builder.get_object("statusLabel"), gameType, filename=filename)
				self.builder.get_object("scoreLabel").set_text("Black: "+str(self.board.blackWins)+" | White: "+str(self.board.whiteWins))
				writeConfigItem("SavePath",os.path.dirname(filename))
				self.builder.get_object("openFileChooser").hide()
				self.builder.get_object("saveToolButton").set_sensitive(True)
				enableAnimations = ea
			except Exception, e:
				print "Error:",e
				if self.infobar != None:
					self.infobar.show()
				else:
					md = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_ERROR, buttons= gtk.BUTTONS_OK, message_format="Error Loading File!\nPlease choose another.")
					md.run()
					md.destroy()
				self.board = GameBoard(self.builder.get_object("gameTable"), self.builder.get_object("statusLabel"), "Local")
				self.builder.get_object("scoreLabel").set_text("Black: 0 | White: 0")
				self.builder.get_object("openFileChooser").present()
		
		else:
			self.newGameDialog()
			self.builder.get_object("openFileChooser").hide()
		
	def prefsOpen(self, widget, event=None):
		#Subroutine to position the menu under the button
		def menuPos(menu, button):
			w = self.builder.get_object("gameWindow").get_position()
			b = button.get_allocation()
			m = menu.get_allocation()
			return (w[0]+b.x+2,w[1]+b.y+b.height+(m.height/2)+2, False)
		
		self.builder.get_object("prefsMenu").popup(None, None, menuPos, 1, 0, widget)

	def prefsClose(self, widget):
		self.builder.get_object("prefsToolButton").set_active(False)
	
	def selectTileSet(self, widget):
		global TileSet
		TileSet = widget.get_label()
		##TODO: refresh board
	
	#Shows the "How To Play" dialog
	def help(self, widget):
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("helpDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("helpDialog").present()

	#Shows the about dialog
	def about(self, widget):
		self.builder.get_object("aboutDialog").set_version(version)
		pos = self.builder.get_object("gameWindow").get_position()
		self.builder.get_object("aboutDialog").move(pos[0]+25, pos[1]+75)
		self.builder.get_object("aboutDialog").present()

	#Hide the "You Won!" dialog and reforms the board appropriately
	def gratsHide(self, widget="NULL", event="NULL"):
		if (widget == self.builder.get_object("sorryDialog")):
			if (self.board.gameType.startswith("Local-AI")):
				reformType = "RTL"
				self.builder.get_object("undoToolButton").set_sensitive(False)
				self.board.reset(reformType)
				self.builder.get_object("statusLabel").set_text("It's Your Turn! ("+self.board.turn+")")
			else :
				self.builder.get_object("statusLabel").set_text("Please wait for Remote Player to start the next Round.")
			#No reform necessary because the user lost.
			self.builder.get_object("sorryDialog").hide()
			
			return
		elif (widget == self.builder.get_object("reformLTRButton")):
			reformType = "LTR"
		elif (widget == self.builder.get_object("reformNormalButton")):
			reformType = "Normal"
		elif ((widget == self.builder.get_object("reformRTLButton")) or (widget == self.builder.get_object("gratsDialog"))):
			reformType = "RTL"
		else :
			print "ERROR: Grats Hide was called be something odd."
		
		self.builder.get_object("undoToolButton").set_sensitive(False)
		self.builder.get_object("gratsDialog").hide()	
		self.board.reset(reformType)
		if (self.board.gameType == "Network"):
			self.connection.reform(reformType)
			self.builder.get_object("statusLabel").set_text("It's the Remote Players turn...")
	
	def toggleAnimations(self, widget):
		global enableAnimations
		enableAnimations = widget.get_active()
		#self.builder.get_object("animationsToggleButton").set_active(enableAnimations)
		#self.builder.get_object("enableAnimationsBox").set_active(enableAnimations)
		writeConfigItem("EnableAnimations",enableAnimations)

	#Starts a thread to update a progress bar repeatedly
	def threadProgressLoop(self, pBarObject, numUpdates, finalCommand=None):
		#Subroutine: moves the progress bar repeatedly
		def progressLoop(pBar, num, cmd):
			num = 20*num
			self.killProgressBar = False
			for i in range(1,num+1):
				if (self.killProgressBar): break
				pBar.set_fraction(float(i)/num)
				time.sleep(0.05)
			if (cmd):
				print "final CMD"
				finalCommand.activate()
		#END: progressLoop()
		threading.Thread(target=progressLoop, args=(pBarObject, numUpdates, finalCommand)).start()

	#Asks the user if they want to update, or tells them they don't have permissions.
	def updateDialog(self, widget="NULL", event="NULL"):
		if (widget == "NULL"):
			#Show updateDialog
			if (os.access(pwd, os.W_OK) and enableUpdates):
				#Write Permissions enabled on Aikisado.py
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
			else :
				#TODO#try to Download zip file instead
				#Access to the file denied
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
			try :
				aikisadoUpdate()
				self.restart()
			except Exception, e:
				#An error has occurred while trying to update.
				print "Error while updating:",e
				#msg = gtk.gdk.TextBuffer()
				msg = self.builder.get_object("downloadFailDetails").get_buffer()
				msg.set_text(str(e))
				self.builder.get_object("downloadFailDetails").set_buffer(msg)
				pos = self.builder.get_object("gameWindow").get_position()
				self.builder.get_object("downloadFailDialog").move(pos[0]+25, pos[1]+75)
				self.builder.get_object("downloadFailDialog").present()

		else :
			self.builder.get_object("updateDialog").hide()
	
	"""Makes the Main window fullscreen or not."""
	def toggleFullscreen(self, widget=None, event=None):
		if (event == None):
			if (enableFullscreen):
				if (self.fullscreen):
					self.builder.get_object("gameWindow").set_resizable(False)	
					processAllGtkEvents()
					self.builder.get_object("gameWindow").unfullscreen()
				else:
					self.builder.get_object("gameWindow").set_resizable(True)
					processAllGtkEvents()
					self.builder.get_object("gameWindow").fullscreen()
		else:
			self.fullscreen = bool(gtk.gdk.WINDOW_STATE_FULLSCREEN & event.new_window_state)

	def confirmExit(self, widget=None):
		"""Gives the user a chance to save the game before exiting."""
		if (not debug):#TODO#Implement way for it to tell if the game has unsaved progress.
			return
		#print "Exit:",self.gameWindowEscape
		if (self.gameWindowEscape):
			print "EXITING!"
			if (widget == None):
				pos = self.builder.get_object("gameWindow").get_position()
				self.builder.get_object("confirmExitDialog").move(pos[0]+25, pos[1]+75)
				self.builder.get_object("confirmExitDialog").present()
			else:
				self.builder.get_object("confirmExitDialog").hide()
		self.gameWindowEscape = True
		#print self.builder.get_object("gameWindow").has_toplevel_focus(), self.builder.get_object("gameWindow").is_active()
		#print self.builder.get_object("gameWindow").get_focus()
		#if self.builder.get_object("gameWindow").has_toplevel_focus():
		#	self.quit()
#			
	
	#Restarts aikisado with the same pid, etc
	def restart(self, widget="NULL"):
		print "Restarting --------------------------------"
		os.execl(os.path.abspath(pwd+"/Aikisado.py"), "0")

	#STUB#Sends/displays chat messages
	def sendChat(self, widget):
		self.builder.get_object("chatBuffer").insert(self.builder.get_object("chatBuffer").get_end_iter(), "\n"+self.builder.get_object("chatEntry").get_text())
		self.builder.get_object("chatEntry").set_text("")
		self.builder.get_object("chatVAdjustment").set_value(self.builder.get_object("chatVAdjustment").get_upper())
	
	#TODO#Write all function comments like this one
	def keyPress(self, widget, event):
		"""Handles a keypress event from the main window.
			These need be handled this way because there not triggered by a button.
			All other mnemonics are handled by accelerators in glade."""
		global debug
		#Press events will repeat if the key is held; Release will not
		if (event.type == gtk.gdk.KEY_PRESS):
			if (event.state & gtk.gdk.CONTROL_MASK):
				if (event.keyval == gtk.keysyms.o):
					#<control>o" = Open (load)
					self.load()
				elif (event.keyval == gtk.keysyms.x):
					#<control>x" = Exit
					self.confirmExit()
				elif (event.keyval == gtk.keysyms.t) and (debug):
					self.board.overlayBoard()
			elif (event.keyval == gtk.keysyms.F11):
				#"F11" = Fullscreen
				self.toggleFullscreen()
			else:
				self.board.moveCursor(event.keyval)
			
			#Konami Code
			if (self.konami != 0):
				if ((self.konami == 1) or (self.konami == 2)) and (event.keyval == gtk.keysyms.Up):#The or is there so that presing up 3 times will not reset the cycle
					self.konami = 2
				elif (self.konami == 2) and (event.keyval == gtk.keysyms.Down):
					self.konami = 3
				elif (self.konami == 3) and (event.keyval == gtk.keysyms.Down):
					self.konami = 4
				elif (self.konami == 4) and (event.keyval == gtk.keysyms.Left):
					self.konami = 5
				elif (self.konami == 5) and (event.keyval == gtk.keysyms.Right):
					self.konami = 6
				elif (self.konami == 6) and (event.keyval == gtk.keysyms.Left):
					self.konami = 7
				elif (self.konami == 7) and (event.keyval == gtk.keysyms.Right):
					self.konami = 8
				elif (self.konami == 8) and (event.keyval == gtk.keysyms.a):
					self.konami = 9
				elif (self.konami == 9) and (event.keyval == gtk.keysyms.b):
					self.konami = 10
				elif (self.konami == 10) and (event.keyval == gtk.keysyms.Return):
					self.konami = 11
				else:
					self.konami = 0
			elif (event.keyval == gtk.keysyms.Up):
				self.konami = 1
		
		elif (event.type == gtk.gdk.KEY_RELEASE):
			if (self.konami == 11) and (event.keyval == gtk.keysyms.Return):
				debug = True
				self.builder.get_object("testingButton").set_visible(True)
				print "Konami!"
			elif (event.keyval == gtk.keysyms.Return) or (event.keyval == gtk.keysyms.Home) or (event.keyval == gtk.keysyms.End):
				self.tilePressed(pos=self.board.cursorPos)
			elif (event.keyval == gtk.keysyms.Escape):
				if (self.fullscreen):
					self.toggleFullscreen()
				else:
					self.confirmExit()
			
#End of class: GameGUI

#Downloads and updates aikisado in-place
def aikisadoUpdate():
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
		if (name[:9] == "Aikisado-"):
			#If the files are already in a folder called aikisado, ignore that folder.
			i = name.index("/")
			goodName = name[i+1:]
		else :
			goodName = name
		if name.endswith('/'):
			#Make the folder
			if ( not os.path.exists(pwd+"/"+goodName)):
				os.mkdir(pwd+"/"+goodName)
		else :
			try:
				#Make the file
				outfile = open(os.path.join(pwd, goodName), 'wb')
			except:
				#Make the folder first =/
				os.mkdir(pwd+"/"+goodName)
				outfile = open(os.path.join(pwd, goodName), 'wb')
			outfile.write(zipFileObject.read(name))
			outfile.close()
	zipFileObject.close()
	
	#Remove Zipfile
	os.remove(pwd+"/AikisadoUpdate.zip")
	print "Update Successful!"
#End of Method aikisadoUpdate 

#This is how it should be; all events are cleared before another animation frame gets displayed.
def processAllGtkEvents():
	#print "doing all"
	while gtk.events_pending():
		gtk.main_iteration(False)

def processOneGtkEvent():
	"""Makes it so that the pandora does not have to work so hard. 
		-If the window is moved are other gtk events show up during animation frames will be skipped!"""
	#print "doing one"
	gtk.main_iteration(False)

def writeConfigItem(var, value):
	"""Writes an item to the config file."""
	config.set("Game",var,value)
	with open(cfgPath,'w') as configfile:
		config.write(configfile)

def Configure():
	"""Read in config info from a file and initialize other default settings"""
	global pwd
	global debug
	global config
	global cfgPath
	global savePath
	global showMoves
	global serverAddress
	global enableUpdates
	global framesPerSquare
	global processGtkEvents
	global enableAnimations
	global enableFullscreen
	config = ConfigParser.RawConfigParser()
	pwd = os.path.abspath(os.path.dirname(__file__)) #location of Aikisado.py
	cfgPath = os.path.abspath(site.USER_BASE+"/share/aikisado/aikisado.cfg")
	
	#Set debug to False if imported, else: False if optimized.
	if __name__ == "__main__":
		debug = __debug__
		print "Debugging:",debug
	else:
		debug = False
	
	#Platform Specific Operations: Set cfgDir & Determine the proper animation settings.
	if (platform.machine() == "armv7l"):
		cfgPath = os.path.abspath(os.getcwd()+"/aikisado.cfg")
		#Because the pandora cant handle too many fps
		processGtkEvents = processOneGtkEvent
		framesPerSquare = 4 #Number of times the image should be refreshed when crossing one square		
		enableAnimations = False #The "ARM" animations are pretty bad still, I don't what the average user to suffer through them =)
		enableFullscreen = True
	else:
		processGtkEvents = processAllGtkEvents
		framesPerSquare = 8
		enableAnimations = True
		enableFullscreen = False
	
	if (debug):
		print "cfgDir:",os.path.dirname(cfgPath)
	
	#Read Config from file and load values.
	try:
		config.read(cfgPath)
		savePath = config.get("Game","SavePath")
		enableAnimations = config.getboolean("Game","EnableAnimations")
		enableFullscreen = config.getboolean("Game","EnableFullscreen")
		showMoves = config.getboolean("Game","ShowMoves")
		enableUpdates = config.getboolean("Game","EnableUpdates")
		serverAddress = config.get("Game","ServerAddress")
	except Exception, e:
		#There is a non-existent or incomplete user config file.
		print "Error loading vals from config file:",e
		print "Making a fresh config file with default values!"
		
		#Initialize default values
		savePath = os.getcwd()
		#enableAnimations = True #Set above in "Platform Specific"
		#enableFullscreen = False
		showMoves =  True
		enableUpdates = True
		serverAddress = "Thanntastic.com"
		
		#Add the defaults the to the config
		if not config.has_section("Game"):
			config.add_section('Game')
		config.set("Game","SavePath",savePath)
		config.set("Game","EnableAnimations",str(enableAnimations))
		config.set("Game","EnableFullscreen",str(enableFullscreen))
		config.set("Game","ShowMoves",str(showMoves))
		config.set("Game","EnableUpdates",str(enableUpdates))
		config.set("Game","ServerAddress",serverAddress)
		
		#Make sure the config dir exists
		if not(os.path.exists(os.path.dirname(cfgPath))):
			os.makedirs(os.path.dirname(cfgPath))
		
		#Write the config file
		with open(cfgPath,'w') as configfile:
			config.write(configfile)

def start():
	"""Basically main(), but doesn't execute if imported."""
	#try:
	Configure()
	gobject.threads_init() #Makes threads work. Formerly "gtk.gdk.threads_init()", but windows really hated it.
	gui = GameGui()
	gtk.main()
	#except Exception, e:
	#	print "Fatal Error:",e
	#finally:
	#	print ""
	#	gui.quit()
		
		
			

#So main wont execute when this module (Aikisado) is imported
if __name__ == "__main__":
	start()
