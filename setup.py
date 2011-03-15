#!/usr/bin/python

from distutils.core import setup

setup (
	name = "Aikisado",
	version = "0.3.2",
	packages = ["Aikisado"],#This puts all of our data in a folder called Aikisado
	author = "Jonathan Knapp (Thann)",
	author_email = "Thann@Linux.com",
	url = "http://sourceforge.net/projects/aikisado/",
	license = "GPLv3",
	description = "Tribute to Kamisado by Burley Games.",
	long_description = "Computerized board game unofficially created in the likeness of Kamisado by Peter Burley of Burley Games.",
	
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
		],
	
	scripts = ["aikisado"],
	package_dir = {"Aikisado":""},
	package_data = {"Aikisado" : ["GUI/*","README.txt","license.txt", "INSTALL*"]}, #these go into the python install directory
	data_files = [("share/pixmaps", ["GUI/aikisado.png"]), ("share/applications",["aikisado.desktop"]), ("share/aikisado", ["README.txt","license.txt", "Aikisado.lnk", "aikisado"])] #these go into "/usr/" or "C:\Python27\"
)
