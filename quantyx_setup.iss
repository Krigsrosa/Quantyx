[Setup]
AppName=Quantyx
AppVersion=1.0
AppPublisher=Quantyx
DefaultDirName={autopf}\Quantyx
DefaultGroupName=Quantyx
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=Quantyx_Installer
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=img\app-ico-1.ico
UninstallDisplayIcon={app}\Quantyx.exe
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "Criar um atalho na Area de Trabalho"; GroupDescription: "Atalhos Adicionais:"

[Files]
Source: "dist\Quantyx\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Quantyx"; Filename: "{app}\Quantyx.exe"; IconFilename: "{app}\_internal\img\app-ico-1.ico"
Name: "{autodesktop}\Quantyx"; Filename: "{app}\Quantyx.exe"; Tasks: desktopicon; IconFilename: "{app}\_internal\img\app-ico-1.ico"

[Run]
Filename: "{app}\Quantyx.exe"; Description: "Iniciar Quantyx"; Flags: nowait postinstall skipifsilent