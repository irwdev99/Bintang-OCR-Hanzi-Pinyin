[Setup]
AppId={{B7A1C2D3-E4F5-6A7B-8C9D-0E1F2A3B4C5D}
AppName=Bintang OCR Hanzi Pinyin
AppVersion=1.0
AppPublisher=Irwan
DefaultDirName={autopf}\BintangOCRHanziPinyin
DefaultGroupName=Bintang OCR Hanzi Pinyin
OutputBaseFilename=Setup_BintangOCRHanziPinyin
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\BintangOCRHanziPinyin.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\Bintang OCR Hanzi Pinyin"; Filename: "{app}\BintangOCRHanziPinyin.exe"
Name: "{group}\Bintang OCR Hanzi Pinyin"; Filename: "{app}\BintangOCRHanziPinyin.exe"
