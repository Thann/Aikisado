start /Wait Installers\1-python-2.7.1.msi
start /Wait Installers\2-pygtk-all-in-one-2.22.6.win32-py2.7.msi

xcopy Aikisado\* C:\Aikisado\ /S /Y
copy Aikisado\Aikisado.lnk %HOMEPATH%\Desktop\
