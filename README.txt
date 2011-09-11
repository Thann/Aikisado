Aikisado is free software realeased under the GPLv3
that you can it download from http://sourceforge.net/projects/aikisado/

Windows install:-----------------------------------
Double-click "INSTALL-Windows.bat"
or install python and pygtk (from installers) then type "python setup.py install",
then type "copy "C:\Python27\share\Aikisado\Aikisado.lnk" "c:%HOMEPATH%\Desktop\""

Linux install:-------------------------------------
Make sure pygtk is installed, Most modern distros will already have this.
In a terminal, as root, type "python setup.py install"
or type "chmod +x INSTALL-Linux.sh" then double-click INSTALL-Linux.sh

Mac OSX:-------------------------------------------
This is NOT currently supprted, but it can be done. Several packages are needed.
Python: Get from http://www.python.org/
PyGTK: compile from source or use MacPorts.
Once you have these run it from terminal or doulble click Aikisado.py

Documentation:-------------------------------------
To get the HTML pydocs just type "python -m pydoc -w ./Aikisado.py"
drop the -w to get the man version

Packaging:-----------------------------------------
Windows(MSI):"setup.py bdist_msi"
Linux(RPM):"./setup.py bdist_rpm"
Linux(PND):Download DistPnd from https://github.com/Tempel/distPND or install from PyPi then run: "./setup.py bdist_pnd"
Update: "setup.py sdist" then rename it to "AikisadoUpdate.zip"
