@echo off
title Sistem Arsip & Dokumen
cd /d "%~dp0"
echo Menjalankan aplikasi dari folder saat ini...
"%~dp0.venv\Scripts\python.exe" -m streamlit run User.py
pause