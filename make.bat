@ECHO OFF

set PWD=%~dp0
set COMMAND=%1
if X%COMMAND%==X set COMMAND=all
if X%COMMAND%==Xhelp goto Help
if X%COMMAND%==Xclean goto Clean
if X%COMMAND%==Xall goto Distro
if X%COMMAND%==Xdistro goto Distro
if X%COMMAND%==Xupload goto Upload
if X%COMMAND%==Xinstall goto Install
if X%COMMAND%==Xuninstall goto UnInstall
goto Help

:Help
echo "Usage: call with args from ['clean', 'all', 'distro', 'upload', 'install', 'uninstall']"
goto End

:Distro
echo.
echo "Building msi installer."
python setup.py bdist_msi
cd ..
if X%COMMAND%==Xall (
  goto Upload
) else (
  goto End
)

:Upload
echo.
echo "Uploading to file server."
cd dist
scp *.msi files@files.yujinrobot.com:pub/appupdater/python/2.7/
cd ..\..
goto End

:Install
python setup.py install --record installed_files.txt
goto End

:UnInstall
SetLocal EnableDelayedExpansion
set UNINSTALL_FILES=
if exist installed_files.txt (
  echo Uninstalling files from the python directories
  echo     Note: it doesn't clean directories.
  for /F "delims=" %%i in (installed_files.txt) do (
    set UNINSTALL_FILES=!UNINSTALL_FILES! %%i
  )
  rem echo !UNINSTALL_FILES!
)
rem Don't know why this won't work inside the if statement.
rm -f %UNINSTALL_FILES%
EndLocal
goto End

:Clean
rd /S /Q %cd%\build
rd /S /Q %cd%\dist
rm -f MANIFEST
rm -f installed_files.txt
goto End

:End
cd %PWD%