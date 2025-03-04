-- Load file excel ke database
-- Langkah penggunaan 
-- 1. buka Terminal, pindah ke direktori ini
-- 2. jalankan psql :
--  $ psql -U postgres
-- 3. buka database olympiae
--  $ \c olympiae2025
-- 4. jalankan query ini
--  $ \i ./create_tables_and_import_data.sql

-- Hapus tabel jika sudah ada
DROP TABLE IF EXISTS podium CASCADE;
DROP TABLE IF EXISTS detail_activities CASCADE;

-- Buat tabel "podium"
CREATE TABLE podium (
    no SERIAL,
    kategori TEXT NOT NULL,
    jenis_kegiatan TEXT NOT NULL,
    nama_team TEXT ,
    bib_peserta TEXT,
    nama_individu TEXT NOT NULL,
    gender TEXT,
    email TEXT,
    tanggal_lahir TEXT,
    usia INTEGER,
    telp TEXT,
    elapsed_time INTERVAL,
    speed NUMERIC NOT NULL,
    jarak NUMERIC NOT NULL,
    pace INTERVAL NOT NULL,
    elevasi INTEGER,
    workout INTEGER NOT NULL,
    finish TEXT NOT NULL,
    angkatan TEXT
);

-- Buat tabel "detail_activities"
CREATE TABLE detail_activities (
    no SERIAL,
    kategori TEXT NOT NULL,
    jenis_kegiatan TEXT NOT NULL,
    nama_team TEXT,
    nama_individu TEXT NOT NULL,
    bib_peserta TEXT,
    link TEXT NOT NULL PRIMARY KEY,
    elapsed_time INTERVAL,
    speed NUMERIC NOT NULL,
    jarak NUMERIC NOT NULL,
    pace INTERVAL NOT NULL,
    elevasi INTEGER,
    hr TEXT,
    average_heartrate NUMERIC,
    tanggal_lari TEXT NOT NULL,
    tanggal_submit TEXT NOT NULL,
    strava_activity_type TEXT,
    flag TEXT
);

-- DATABASE LOKAL
-- Import data ke dalam tabel "podium"
-- \copy podium FROM './input/podium.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';');

-- Import data ke dalam tabel "detail_activities"
-- \copy detail_activities FROM './input/detail_activities.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';');

-- DATABASE DIGITAL OCEAN
-- Import data ke dalam tabel "podium"
\copy podium FROM '/var/lib/postgresql/import/input/podium.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';');

-- Import data ke dalam tabel "detail_activities"
\copy detail_activities FROM '/var/lib/postgresql/import/input/detail_activities.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';');
