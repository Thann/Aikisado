#!/usr/bin/python

from distutils.core import setup

setup (
	name = "Aikisado",
	version = "0.3.1",
	packages = [""],
	author = "Jonathan Knapp (Thann)",
	author_email = "Thann@Linux.com",
	url = "http://sourceforge.net/projects/aikisado/",
	license = "GPLv3",
	description = "Computerized board game unofficially created in the likeness of Kamisado by Peter Burley of Burley Games.",
	#long_description= "Long description of the package",
	
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: X11 Applications :: GTK',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		"Natural Language :: English"
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python',
		'Topic :: Games/Entertainment :: Board Games',
		'Topic :: Games/Entertainment :: Puzzle Games'
		],
	
	scripts = ["aikisdo/CreateShortcuts.py"],
	data_files = [
		("", ["README.txt","license.txt"]),
		#("",["aikisado/Aikisado.pyw","aikisado/Aikisado.lnk","aikisado/license.txt","aikisado/README.txt","aikisado/INSTALL-Windows.bat"]),
		#("GUI",["aikisado/GUI/*.jpg"])
		("GUI",["GUI/BlueBG.jpg", "GUI/BlueBlackPiece.png", "GUI/BlueWhitePiece.png", "GUI/BrownBG.jpg", "GUI/BrownBlackPiece.png", "GUI/BrownWhitePiece.png", "GUI/drawing.svg", "GUI/EligibleMarkGrey.png", "GUI/EligibleMark.png", "GUI/GreenBG.jpg", "GUI/GreenBlackPiece.png", "GUI/GreenWhitePiece.png", "GUI/Icon.bmp", "GUI/Icon.png", "GUI/Images.xcf", "GUI/main.ui", "GUI/OrangeBG.jpg", "GUI/OrangeBlackPiece.png", "GUI/OrangeWhitePiece.png", "GUI/PinkBG.jpg", "GUI/PinkBlackPiece.png", "GUI/PinkWhitePiece.png", "GUI/PurpleBG.jpg", "GUI/PurpleBlackPiece.png", "GUI/PurpleWhitePiece.png", "GUI/RedBG.jpg", "GUI/RedBlackPiece.png", "GUI/RedWhitePiece.png", "GUI/SelectedMark.png", "GUI/SumoBlack.png", "GUI/SumoPushDown.png", "GUI/SumoPushUp.png", "GUI/SumoSuperBlack-old.png", "GUI/SumoSuperBlack.png", "GUI/SumoSuperWhite-old.png", "GUI/SumoSuperWhite.png", "GUI/SumoWhite.png", "GUI/YellowBG.jpg", "GUI/YellowBlackPiece.png", "GUI/YellowWhitePiece.png"])
		]
)
