# define the name of the installer
Outfile "EPLaunchInstall.exe"

# define the directory to install to, the desktop in this case as specified
# by the predefined $DESKTOP variable
InstallDir $DESKTOP

# default section
Section

# define the output path for this file
SetOutPath $INSTDIR

# define what to install and place it in the output path
File /r dist\EPLaunch

SectionEnd