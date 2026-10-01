import os
import sys

# Garante que consegue importar utils.version se executado da raiz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.version import __version__

content = f"""[Setup]
AppName=Quantyx
AppVersion={__version__}
AppPublisher=Quantyx
DefaultDirName={{autopf}}\Quantyx
DefaultGroupName=Quantyx
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=Quantyx_Installer_{__version__}
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=img\\app-ico-1.ico
UninstallDisplayIcon={{app}}\Quantyx.exe
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "Criar um atalho na Area de Trabalho"; GroupDescription: "Atalhos Adicionais:"

[Files]
Source: "dist\Quantyx\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\Quantyx"; Filename: "{{app}}\Quantyx.exe"; IconFilename: "{{app}}\\_internal\img\\app-ico-1.ico"
Name: "{{autodesktop}}\Quantyx"; Filename: "{{app}}\Quantyx.exe"; Tasks: desktopicon; IconFilename: "{{app}}\\_internal\img\\app-ico-1.ico"

[Run]
Filename: "{{app}}\Quantyx.exe"; Description: "Iniciar Quantyx"; Flags: nowait postinstall skipifsilent"""

with open("quantyx_setup.iss", "w", encoding="utf-8") as f:
    f.write(content)
