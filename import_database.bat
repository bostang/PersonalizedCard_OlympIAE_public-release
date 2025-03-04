@echo off
echo Mengimpor data dari excel ke PostgreSQL...

:: Pastikan bahwa di dalam difolder ./input terdapat file podium.csv dan detail_activities.csv

:: 1. Login ke database PostgreSQL dan jalankan skrip SQL
psql -U postgres -d olympiae2025 -f create_tables_and_import_data.sql

:: 2. Periksa apakah ada error
if %errorlevel% neq 0 (
    echo Terjadi kesalahan saat mengimpor data.
) else (
    echo Data berhasil diimpor ke database olympiae2025.
)

pause
