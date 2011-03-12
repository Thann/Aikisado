#!/usr/bin/python

from distutils.core import setup
import Aikisado
import platform

if (platform.system() == "Windows"):
	data = []#[("Aikisado",["Aikisado.lnk"])]
else :
	data = [("share/icons/gnome/48x48/apps", ["GUI/Aikisado.png"]), ("share/applications",["aikisado.desktop"])] #these go into /usr/

setup (
	name = "Aikisado",
	version = Aikisado.version,
	packages = ["Aikisado"],#"Aikisado"
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
		],
	
	scripts = ["aikisado"],
	package_dir = {"Aikisado":""},
	package_data = {"Aikisado" : ["GUI/*","README.txt","license.txt"]},
	data_files = data
)
