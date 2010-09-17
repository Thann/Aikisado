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

import sys, os, urllib2, zipfile

def update():

	pwd = os.path.dirname(sys.argv[0])
	print "pwd: "+pwd
	##Download File
	print "Downloading file..."
	#zipFileURL = urllib2.urlopen("http://downloads.sourceforge.net/project/aikisado/Aikisado.zip")
	#zipFile = open(pwd+"/AikisadoUpdate.zip", "wb")
	#zipFile.write(zipFileURL.read())
	#zipFile.close()
	print "Download Complete! "
	##UnZip File
	zipFileObject = zipfile.ZipFile(pwd+"/AikisadoUpdate.zip")
	for name in zipFileObject.namelist():
		print "name: "+name
		if name.endswith('/'):
		    os.mkdir(pwd+"/Update/"+name)
		else:
		    outfile = open(self.os.path.join(pwd+"/Update", name), 'wb')
		    outfile.write(zfobj.read(name))
		    outfile.close()
	##Install File

print "Updating to latest verion."
update()