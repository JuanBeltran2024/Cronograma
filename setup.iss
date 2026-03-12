[Setup]
AppName=Cronograma Universitario
AppVersion=1.0
DefaultDirName={autopf}\CronogramaUniversitario
DefaultGroupName=Cronograma Universitario
OutputDir=Output
OutputBaseFilename=Instalador_Cronograma
Compression=lzma
SolidCompression=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Cronograma Universitario"; Filename: "{app}\app.exe"
Name: "{autodesktop}\Cronograma Universitario"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\app.exe"; Description: "{cm:LaunchProgram,Cronograma Universitario}"; Flags: nowait postinstall skipifsilent
