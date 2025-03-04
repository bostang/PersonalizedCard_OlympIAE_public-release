\set VERBOSITY verbose

\echo '----- KATEGORI : TOTAL JARAK TERJAUH -----'
-- LARI QUATRO JARAK TERJAUH
\echo 'RUN QUATRO TOTAL JARAK TERJAUH'
SELECT
    ROW_NUMBER() OVER (ORDER BY SUM(jarak) DESC) AS rank,
    nama_team,
    SUM(jarak) as total_jarak
FROM
    detail_activities
WHERE
    kategori LIKE '170K RUN TEAM OF 4'
GROUP BY
    nama_team
ORDER BY
    SUM(jarak) DESC
LIMIT 2;

-- RUN DUO JARAK TERJAUH
\echo 'RUN DUO TOTAL JARAK TERJAUH'
SELECT 
    ROW_NUMBER() OVER (ORDER BY SUM(jarak) DESC) AS rank,
    nama_team,
    SUM(jarak)  as total_jarak
FROM
    detail_activities
WHERE
    kategori LIKE '85K RUN DUO'
GROUP BY
    nama_team
ORDER BY
    SUM(jarak) DESC
LIMIT 2;

-- RUN SOLO JARAK TERJAUH
\echo 'RUN SOLO TOTAL JARAK TERJAUH'
SELECT 
    ROW_NUMBER() OVER (ORDER BY SUM(jarak) DESC) AS rank,
    bib_peserta,
    nama_individu,
    SUM(jarak) AS total_jarak
FROM
    detail_activities
WHERE
    kategori ILIKE '42,2K RUN SOLO'
GROUP BY
    bib_peserta, nama_individu
ORDER BY
    total_jarak DESC
LIMIT 2;

-- BIKE SOLO JARAK TERJAUH
\echo 'BIKE SOLO TOTAL JARAK TERJAUH'
SELECT
    ROW_NUMBER() OVER (ORDER BY SUM(jarak) DESC) AS rank,
    bib_peserta,
    nama_individu,
    SUM(jarak) AS total_jarak
FROM
    detail_activities
WHERE
    kategori ILIKE '180K RIDE SOLO'
GROUP BY
    bib_peserta,
    nama_individu
ORDER BY
    total_jarak DESC
LIMIT 1;

\echo '----- KATEGORI : TOTAL ELEVASI TERTINGGI -----'

-- TOTAL ELEVASI TERTINGGI (LARI)
\echo 'TOTAL ELEVASI TERTINGGI (LARI)'
SELECT
    ROW_NUMBER() OVER (ORDER BY SUM(elevasi) DESC) AS rank,
    bib_peserta,
    nama_individu,
    SUM(elevasi) AS total_elevasi
FROM
    detail_activities
WHERE
    jenis_kegiatan ILIKE 'Run'
GROUP BY
    bib_peserta,
    nama_individu
ORDER BY
    total_elevasi DESC
LIMIT 1;

-- TOTAL ELEVASI TERTINGGI (SEPEDA)
\echo 'TOTAL ELEVASI TERTINGGI (SEPEDA)'
SELECT
    ROW_NUMBER() OVER (ORDER BY SUM(elevasi) DESC) AS rank,
    bib_peserta,
    nama_individu,
    SUM(elevasi) AS total_elevasi
FROM
    detail_activities
WHERE
    jenis_kegiatan ILIKE 'Ride'
GROUP BY
    bib_peserta,
    nama_individu
ORDER BY
    total_elevasi DESC
LIMIT 1;

\echo '----- KATEGORI : SINGLE ACTIVITY TERLAMA -----'

-- SINGLE ACTIVITY TERLAMA (LARI)
\echo 'SINGLE ACTIVITY TERLAMA (LARI)'
SELECT
    ROW_NUMBER() OVER (ORDER BY elapsed_time DESC) AS rank,
    bib_peserta,
    nama_individu,
    elapsed_time,
    speed
FROM
    detail_activities
WHERE
    jenis_kegiatan ILIKE 'Run' and speed > 1
    -- speed > 1 : mencegah aktivitas yang AFK
ORDER BY
    elapsed_time DESC
LIMIT 1;

-- SINGLE ACTIVITY TERLAMA (SEPEDA)
\echo 'SINGLE ACTIVITY TERLAMA (SEPEDA)'
SELECT
    ROW_NUMBER() OVER (ORDER BY elapsed_time DESC) AS rank,
    bib_peserta,
    nama_individu,
    elapsed_time,
    speed
FROM
    detail_activities
WHERE
    jenis_kegiatan ILIKE 'Ride' and speed > 7
    -- speed > 7 : mencegah aktivitas yang AFK
ORDER BY
    elapsed_time DESC
LIMIT 1;

\echo '----- KATEGORI : SINGLE ACTIVITY TERTINGGI -----'
-- SINGLE ACTIVITY ELEVASI TERTINGGI (LARI)
\echo 'SINGLE ACTIVITY ELEVASI TERTINGGI (LARI)'
SELECT
    ROW_NUMBER() OVER (ORDER BY elevasi DESC) AS rank,
    bib_peserta,
    nama_individu,
    elevasi,
    speed
FROM
    detail_activities
WHERE
    jenis_kegiatan ILIKE 'Run'
ORDER BY
    elevasi DESC
LIMIT 1;

-- SINGLE ACTIVITY ELEVASI TERTINGGI (SEPEDA)
\echo 'SINGLE ACTIVITY ELEVASI TERTINGGI (SEPEDA)'
SELECT
    ROW_NUMBER() OVER (ORDER BY elevasi DESC) AS rank,
    bib_peserta,
    nama_individu,
    elevasi,
    speed
FROM
    detail_activities
WHERE
    jenis_kegiatan ILIKE 'Ride'
ORDER BY
    elevasi DESC
LIMIT 1;

\echo '----- KATEGORI : SINGLE ACTIVITY TERJAUH -----'

-- SINGLE ACTIVITY TERJAUH (LARI)
\echo 'SINGLE ACTIVITY TERJAUH (LARI)'
SELECT
    ROW_NUMBER() OVER (ORDER BY jarak DESC) AS rank,
    bib_peserta,
    nama_individu,
    jarak,
    speed
FROM
    detail_activities
WHERE
    jenis_kegiatan ILIKE 'Run' and speed > 1
    -- speed > 1 : mencegah aktivitas yang AFK
ORDER BY
    jarak DESC
LIMIT 1;

-- SINGLE ACTIVITY ELEVASI TERJAUH (SEPEDA)
\echo 'SINGLE ACTIVITY ELEVASI TERJAUH (SEPEDA)'
SELECT
    ROW_NUMBER() OVER (ORDER BY jarak DESC) AS rank,
    bib_peserta,
    nama_individu,
    jarak,
    speed
FROM
    detail_activities
WHERE
    jenis_kegiatan ILIKE 'Ride' and speed > 7
    -- speed > 7 : mencegah aktivitas yang AFK
ORDER BY
    jarak DESC
LIMIT 1;


\echo '----- KATEGORI : SINGLE ACTIVITY TERJAUH (SENIOR SPECIAL AWARD) -----'

-- SINGLE ACTIVITY TERJAUH (LARI)
\echo 'SINGLE ACTIVITY TERJAUH (LARI) [SENIOR]'
SELECT
    ROW_NUMBER() OVER (ORDER BY da.jarak DESC) AS rank,
    da.bib_peserta,
    da.nama_individu,
    da.jarak,
    da.speed,
    CASE
        WHEN p.angkatan ~ '^[0-9]+$' THEN CAST(p.angkatan AS INTEGER)
        ELSE NULL
    END AS angkatan_peserta
FROM
    detail_activities da
JOIN
    podium p ON da.bib_peserta = p.bib_peserta
WHERE
    da.jenis_kegiatan ILIKE 'Run'
    AND da.speed > 1
    AND CASE
        WHEN p.angkatan ~ '^[0-9]+$' THEN CAST(p.angkatan AS INTEGER)
        ELSE NULL
    END < 1990
ORDER BY
    da.jarak DESC
LIMIT 1;

-- SINGLE ACTIVITY TERJAUH (SEPEDA)
\echo 'SINGLE ACTIVITY TERJAUH (SEPEDA) [SENIOR]'
SELECT
    ROW_NUMBER() OVER (ORDER BY da.jarak DESC) AS rank,
    da.bib_peserta,
    da.nama_individu,
    da.jarak,
    da.speed,
    CASE
        WHEN p.angkatan ~ '^[0-9]+$' THEN CAST(p.angkatan AS INTEGER)
        ELSE NULL
    END AS angkatan_peserta
FROM
    detail_activities da
JOIN
    podium p ON da.bib_peserta = p.bib_peserta
WHERE
    da.jenis_kegiatan ILIKE 'Ride'
    AND da.speed > 1
    AND CASE
        WHEN p.angkatan ~ '^[0-9]+$' THEN CAST(p.angkatan AS INTEGER)
        ELSE NULL
    END < 1990
ORDER BY
    da.jarak DESC
LIMIT 1;

\echo '----- KATEGORI : SINGLE ACTIVITY TERCEPAT (SENIOR SPECIAL AWARD) -----'

-- SINGLE ACTIVITY TERCEPAT (LARI)
\echo 'SINGLE ACTIVITY TERCEPAT (LARI) [SENIOR]'
SELECT
    ROW_NUMBER() OVER (ORDER BY da.speed DESC) AS rank,
    da.bib_peserta,
    da.nama_individu,
    da.speed,
    da.speed,
    CASE
        WHEN p.angkatan ~ '^[0-9]+$' THEN CAST(p.angkatan AS INTEGER)
        ELSE NULL
    END AS angkatan_peserta
FROM
    detail_activities da
JOIN
    podium p ON da.bib_peserta = p.bib_peserta
WHERE
    da.jenis_kegiatan ILIKE 'Run'
    AND CASE
        WHEN p.angkatan ~ '^[0-9]+$' THEN CAST(p.angkatan AS INTEGER)
        ELSE NULL
    END < 1990
ORDER BY
    da.speed DESC
LIMIT 1;

-- SINGLE ACTIVITY TERCEPAT (SEPEDA)
\echo 'SINGLE ACTIVITY TERCEPAT (SEPEDA) [SENIOR]'
SELECT
    ROW_NUMBER() OVER (ORDER BY da.speed DESC) AS rank,
    da.bib_peserta,
    da.nama_individu,
    da.speed,
    CASE
        WHEN p.angkatan ~ '^[0-9]+$' THEN CAST(p.angkatan AS INTEGER)
        ELSE NULL
    END AS angkatan_peserta
FROM
    detail_activities da
JOIN
    podium p ON da.bib_peserta = p.bib_peserta
WHERE
    da.jenis_kegiatan ILIKE 'Ride'
    AND CASE
        WHEN p.angkatan ~ '^[0-9]+$' THEN CAST(p.angkatan AS INTEGER)
        ELSE NULL
    END < 1990
ORDER BY
    da.speed DESC
LIMIT 1;