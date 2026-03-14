; ========================================
; MyUniTasks - Inno Setup Script
; ========================================

#define MyAppName "MyUniTasks"
#define MyAppVersion "1.0"
#define MyAppPublisher "Juan Beltran"
#define MyAppExeName "MyUniTasks.exe"
#define SourceDir "C:\Users\juanm\Desktop\Yo\Cronograma\dist\MyUniTasks"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=C:\Users\juanm\Desktop\Yo\Cronograma\installer
OutputBaseFilename=MyUniTasks_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Makes the installer look modern and clean
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=
PrivilegesRequired=lowest

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el Escritorio"; GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Files]
; Bundle all files from PyInstaller output
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName}"; Flags: nowait postinstall skipifsilent
