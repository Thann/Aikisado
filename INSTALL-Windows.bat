REM IF EXIST Installers GOTO FULLINSTALL

GOTO FULLINSTALL

:JUSTGAMEPY
setup.py install
copy "C:\Python27\share\aikisado\Aikisado.lnk" "c:%HOMEPATH%\Desktop\"
C:\Python27\Lib\site-packages\Aikisado\Aikisado.lnk
exit

:JUSTGAMEEXE
start /Wait Installers\Aikisado-0.3.2.win32.exe
copy "Installers\Aikisado.lnk" "c:%HOMEPATH%\Desktop\"
installers\Aikisado.lnk
exit

:FULLINSTALL
start /Wait Installers\1-python-2.7.1.msi
start /Wait Installers\2-pygtk-all-in-one-2.22.6.win32-py2.7.msi
start /Wait Installers\Aikisado-0.3.2.win32.exe
copy "Installers\Aikisado.lnk" "c:%HOMEPATH%\Desktop\"
installers\Aikisado.lnk
exit
