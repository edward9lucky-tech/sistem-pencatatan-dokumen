@echo off
title Menjalankan Aplikasi GasPYthon
echo Sedang mencari lokasi folder proyek di komputer ini...

:: Mencari drive mana yang memiliki folder My Drive\GasPYthon
for %%d in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%d:\My Drive\GasPYthon\User.py" (
        set "TARGET_DRIVE=%%d"
        goto :found
    )
    if exist "%%d:\Google Drive\GasPYthon\User.py" (
        set "TARGET_DRIVE=%%d"
        goto :found
    )
)

echo [ERROR] Folder GasPYthon tidak ditemukan di komputer ini!
pause
exit

:found
echo Ditemukan di Drive %TARGET_DRIVE%! Memulai aplikasi...
%TARGET_DRIVE%:
cd "\My Drive\GasPYthon" 2>nul
cd "\Google Drive\GasPYthon" 2>nul

py -m streamlit run User.py
pause