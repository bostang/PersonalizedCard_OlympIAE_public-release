# Import Library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import traceback


from common import *

# Implementasi Fungsi/Prosedur

import pandas as pd

import pandas as pd

def get_target_reach_date(nama_team, df_detail, target_distance=42.2):
    """
    Menentukan tanggal pertama kali tim mencapai target_distance secara kronologis.

    Args:
        nama_team (str): Nama tim peserta.
        df_detail (pd.DataFrame): Data aktivitas peserta.
        target_distance (float): Jarak target dalam km (default: 42.2 km untuk lari, 180 km untuk sepeda).

    Returns:
        datetime or None: Tanggal pencapaian target atau None jika tidak tercapai.
    """
    # Filter data berdasarkan nama tim
    df = df_detail[df_detail["nama_team"] == nama_team].copy()

    if df.empty:
        return None  # Jika tidak ada data, kembalikan None
    
    # Konversi tanggal ke datetime
    df["tanggal_submit"] = pd.to_datetime(df["tanggal_submit"], errors="coerce", format='%d/%m/%Y %H:%M:%S')

    # Urutkan berdasarkan tanggal_submit (kronologis)
    df = df.sort_values(by="tanggal_submit")

    # Inisialisasi variabel
    total_distance = 0

    # Iterasi aktivitas secara kronologis
    for _, row in df.iterrows():
        total_distance += row["jarak"]

        # Jika sudah mencapai target, kembalikan tanggal aktivitas terakhir yang dihitung
        if total_distance >= target_distance:
            return row["tanggal_submit"]

    return None  # Jika target tidak tercapai, kembalikan None

def save_all_teams_stats_to_csv(df_detail, output_filename="./output/olympiae2025_final_result_team.csv"):
    """
    Menghitung statistik terbaik untuk semua tim berdasarkan kategori dan menyimpan hasilnya ke dalam file CSV.

    Args:
        df_detail (pd.DataFrame): Data aktivitas peserta.
        output_filename (str, optional): Nama file CSV untuk menyimpan hasil (default: "./output/team_stats.csv").
    """
    # Dapatkan daftar unik tim dan kategori dari dataframe
    unique_teams = df_detail[["nama_team", "kategori"]].dropna().drop_duplicates()

    # Mapping kategori ke target distance
    category_target_distances = {
        "170K RUN TEAM OF 4": 170.0,
        "85K RUN DUO": 85.0,
        "540K RIDE TEAM OF 4": 540.0
    }

    # List untuk menyimpan hasil
    results = []

    for _, row in unique_teams.iterrows():
        team = row["nama_team"]
        category = row["kategori"]

        # Tentukan target jarak berdasarkan kategori
        target_distance = category_target_distances.get(category, 42.2)  # Default 42.2 km jika kategori tidak dikenal

        stats = get_best_activity_stats_team(team, df_detail, target_distance)
        target_reach_date = get_target_reach_date(team, df_detail, target_distance)

        # Pastikan hasil tidak mengandung error sebelum menyimpan
        if "error" not in stats:
            results.append({
                "Team": stats["Team"],
                "Category": category,
                "Total Distance": f"{stats['Total Distance']:.2f}",
                "Total Time": stats["Total Time"],
                "Average Speed": f"{stats['Average Speed']:.2f}",
                "estimated_time_for_target_distance": str(stats["estimated_time_for_target_distance"])[:-7],  # Potong mikrodetik
                "Target Reach Date": target_reach_date

            })

    # Konversi hasil ke DataFrame
    df_results = pd.DataFrame(results)

    # Simpan ke CSV dengan separator ';'
    df_results.to_csv(output_filename, index=False, sep=";")

    print(f"✅ Hasil perlombaan peserta (kategori tim) telah disimpan ke {output_filename}")

def get_best_activity_stats_team(nama_team, df_detail, target_distance=42.2):
    """
    Menentukan kombinasi aktivitas terbaik berdasarkan kecepatan tertinggi 
    hingga mencapai jarak tertentu (default: 42.2 km untuk lari, 180 km untuk sepeda) 
    untuk seluruh anggota tim.

    Args:
        nama_team (str): Nama tim peserta.
        df_detail (pd.DataFrame): Data aktivitas peserta.
        target_distance (float): Jarak target dalam km (default: 42.2 km untuk lari, 180 km untuk sepeda).

    Returns:
        dict: Statistik aktivitas terbaik tim, termasuk total jarak, waktu, rata-rata speed,
              estimasi waktu untuk menempuh target_distance, dan tanggal pencapaian target.
    """
    # Filter data berdasarkan nama tim
    df = df_detail[df_detail["nama_team"] == nama_team].copy()

    if df.empty:
        return {"error": f"Tidak ada data untuk tim {nama_team}"}
    
    # Konversi waktu ke timedelta
    df["elapsed_time"] = pd.to_timedelta(df["elapsed_time"], errors="coerce")

    # Pastikan kolom 'tanggal' dalam format datetime

    df["tanggal_submit"] = pd.to_datetime(df["tanggal_submit"], errors="coerce", format='%d/%m/%Y %H:%M:%S')


    # Urutkan berdasarkan speed tertinggi
    df = df.sort_values(by="speed", ascending=False)

    # Pilih aktivitas dengan speed tertinggi hingga total jarak >= target_distance
    selected_activities = []
    total_distance = 0
    total_time = pd.Timedelta(0)
    total_speed = 0
    activity_count = 0

    for _, row in df.iterrows():
        if total_distance >= target_distance:
            break
        selected_activities.append(row)
        total_distance += row["jarak"]
        total_time += row["elapsed_time"]
        total_speed += row["speed"]
        activity_count += 1

    # Hitung rata-rata speed
    avg_speed = total_speed / activity_count if activity_count > 0 else 0

    # Estimasi waktu untuk Target Jarak
    normalized_time = pd.to_timedelta(target_distance / avg_speed, unit="h") if avg_speed > 0 else pd.Timedelta(0)
        
    return {
        "Team": nama_team,
        "Total Distance": total_distance,
        "Total Time": total_time,
        "Average Speed": avg_speed,
        "estimated_time_for_target_distance": normalized_time,
        "Selected Activities": selected_activities,
    }

def save_participant_data_to_csv(df_detail, df_podium, output_file="./output/olympiae2025_final_result_solo.csv"):
    """
    Menyimpan data peserta (1-303) ke dalam file CSV dengan informasi:
    - Nama
    - Kategori (hanya 180K RIDE dan 42.2K RUN)
    - Tanggal Finish (dari get_date_when_reaching_target)
    - Minimum Elapsed Time Target (dari get_best_activity_stats)
    
    Parameter:
    - df_detail: DataFrame utama yang berisi informasi peserta
    - df_podium: DataFrame yang diperlukan untuk fungsi tanggal finish
    - output_file: Nama file CSV output
    """

    # Hanya proses peserta dalam kategori 180K RIDE dan 42.2K RUN
    valid_categories = {"180K RIDE SOLO", "42.2K RUN SOLO"}
    df_podium_filtered = df_podium[df_podium["kategori"].astype(str).isin(valid_categories)]

    # List untuk menyimpan hasil
    data_list = []

    # Mapping kategori ke target distance
    category_target_distances = {
        "42.2K RUN SOLO": 42.2,
        "180K RIDE SOLO": 180
    }
    

    # Iterasi setiap peserta yang valid
    for index, row in df_podium_filtered.iterrows():
        bib_number = int(row["bib_peserta"])

        # Pastikan BIB tidak kosong
        if pd.isna(bib_number):
            print(f"⚠️ Melewati peserta tanpa BIB pada index {index}")
            continue

        category = row["kategori"]

        # Tentukan target jarak berdasarkan kategori
        target_distance = category_target_distances.get(category, 42.2)  # Default 42.2 km jika kategori tidak dikenal

        # Dapatkan tanggal finish
        hasil_pencapaian = get_date_when_reaching_target(bib_number=bib_number, df_detail=df_detail, df_podium=df_podium)
        tanggal_finish = hasil_pencapaian.get("Tanggal Pencapaian", "Tidak Ditemukan")

        # Dapatkan minimum elapsed time target
        best_stats = get_best_activity_stats(bib_number=bib_number, df_detail=df_detail, target_distance=target_distance)
        minimum_elapsed_time_target = best_stats.get("estimated_time_for_target_distance", "Tidak Ditemukan")
        total_jarak = round(best_stats.get("Total Distance", 0),2)
        total_time = best_stats.get("Total Time", "Tidak Ditemukan")
        average_speed = round(best_stats.get("Average Speed", 0),2)
    

        # Tambahkan ke list hasil
        data_list.append([
            row["bib_peserta"],
            row["nama_individu"],
            row["kategori"],
            total_jarak,
            total_time,
            average_speed,
            tanggal_finish,
            minimum_elapsed_time_target
        ])

    # Konversi ke DataFrame
    df_output = pd.DataFrame(data_list, columns=["BIB Peserta", "Nama", "Kategori", "Total Jarak", "Total Waktu", "Average Speed", "Tanggal Finish", "Minimum Elapsed Time Target"])

    # Simpan ke CSV
    df_output.to_csv(output_file, index=False, encoding="utf-8", sep=";")

    print(f"✅ Hasil perlombaan peserta (kategori 180K RIDE & 42.2K RUN) telah disimpan ke {output_file}")

def get_best_activity_stats(bib_number, df_detail, target_distance=42.2):
    """
    Menentukan kombinasi aktivitas terbaik berdasarkan kecepatan tertinggi 
    hingga mencapai jarak tertentu (default: 42.2 km (lari) , sepeda : 180km).

    Args:
        bib_number (int): Nomor BIB peserta.
        df_detail (pd.DataFrame): Data aktivitas peserta.
        target_distance (float): Jarak target dalam km (default: 42.2 km,  sepeda : 180km).

    Returns:
        dict: Statistik aktivitas terbaik, termasuk total jarak, waktu, rata-rata speed,
              serta estimasi waktu untuk menempuh 42.2 km (lari) atau 180km (sepeda).
    """
    # Filter data berdasarkan nomor BIB
    df = df_detail[df_detail["bib_peserta"] == f"{bib_number:04d}"].copy()
    
    if df.empty:
        return {"error": f"Tidak ada data untuk BIB {bib_number}"}
    
    # Konversi waktu ke timedelta
    df["elapsed_time"] = pd.to_timedelta(df["elapsed_time"], errors="coerce")

    # Urutkan berdasarkan speed tertinggi
    df = df.sort_values(by="speed", ascending=False)

    # Pilih aktivitas dengan Speed tertinggi hingga total jarak >= target_distance
    selected_activities = []
    total_distance = 0
    total_time = pd.Timedelta(0)
    total_speed = 0

    for _, row in df.iterrows():
        if total_distance >= target_distance:
            break
        selected_activities.append(row)
        total_distance += row["jarak"]
        total_time += row["elapsed_time"]
        total_speed += row["speed"]

    # Hitung rata-rata speed
    avg_speed = total_speed / len(selected_activities) if selected_activities else 0

    # Estimasi waktu untuk Target Jarak
    normalized_time = pd.to_timedelta(target_distance / avg_speed, unit="h") if avg_speed > 0 else pd.Timedelta(0)
        
    return {
        "BIB": bib_number,
        "Total Distance": total_distance,
        "Total Time": total_time,
        "Average Speed": avg_speed,
        "estimated_time_for_target_distance": normalized_time,
        "Selected Activities": selected_activities,
    }

def get_date_when_reaching_target(bib_number, df_detail, df_podium):
    """
    Menentukan tanggal ketika peserta dengan nomor BIB tertentu mencapai total jarak target 
    berdasarkan kategori lomba.

    Args:
        bib_number (int): Nomor BIB peserta.
        df_detail (pd.DataFrame): Data aktivitas peserta.
        df_podium (pd.DataFrame): Data peserta lomba dengan kategori lomba.

    Returns:
        dict: Berisi BIB peserta, kategori lomba, target jarak, tanggal pencapaian target, 
              dan total jarak yang ditempuh.
    """
    # Dapatkan informasi peserta dari df_podium
    nama_peserta, _, _, _, _, _, _, _, kategori, _, _ = get_statistik_peserta(f"{bib_number:04d}", df_podium)
    
    if not nama_peserta:
        return {"BIB": bib_number, "Kategori": None, "Target Distance": None, "Tanggal Pencapaian": None, "Status": "Peserta tidak ditemukan"}

    # Tentukan target jarak berdasarkan kategori lomba
    kategori_lomba = {
        "180K RIDE SOLO": 180,
        "170K RUN TEAM OF 4": 170,
        "85K RUN DUO": 85,
        "540K RIDE TEAM OF 4": 540,
        "42.2K RUN SOLO": 42.2  # Jika ada kategori sepeda
    }
    target_distance = kategori_lomba.get(kategori, 42.2)  # Default ke 42.2 km jika kategori tidak dikenal

    # Filter data berdasarkan nomor BIB
    df_peserta = df_detail[df_detail["bib_peserta"] == f"{bib_number:04d}"].copy()

    if df_peserta.empty:
        return {"BIB": bib_number, "Kategori": kategori, "Target Distance": target_distance, "Tanggal Pencapaian": None, "Status": "Tidak ada data aktivitas"}

    # Konversi tanggal ke format datetime
    df_peserta["tanggal_submit"] = pd.to_datetime(df_peserta["tanggal_submit"], format='%d/%m/%Y %H:%M:%S', errors="coerce")

    # Pastikan data diurutkan berdasarkan tanggal submit
    df_peserta = df_peserta.sort_values(by="tanggal_submit")

    # Hitung jarak kumulatif
    df_peserta["jarak_kumulatif"] = df_peserta["jarak"].cumsum()

    # Cari baris pertama yang mencapai target jarak
    mencapai_target = df_peserta[df_peserta["jarak_kumulatif"] >= target_distance]

    if not mencapai_target.empty:
        tanggal_target = mencapai_target.iloc[0]["tanggal_submit"]
        return {
            "BIB": bib_number,
            "Nama": nama_peserta,
            "Kategori": kategori,
            "Target Distance": target_distance,
            "Tanggal Pencapaian": tanggal_target.strftime("%Y-%m-%d %H:%M:%S"),
            "Status": "Target tercapai",
        }
    else:
        return {
            "BIB": bib_number,
            "Nama": nama_peserta,
            "Kategori": kategori,
            "Target Distance": target_distance,
            "Tanggal Pencapaian": None,
            "Status": "Belum mencapai target",
        }

def generate_complete_data(bib_number, df_detail, df_podium, data_path, verbose):
    """
    Menghasilkan analisis data lengkap untuk seorang peserta berdasarkan nomor BIB mereka.
    Mencakup : 
    facts_about_you,
    agregate_statistics,
    scatter_speed, scatter_distance, scatter_elev_gain, scatter_elapsed_time,
    finish_proportion, 
    finish_per_year_histogram,
    activity_table,
    activity_barplot,
    cumulative_distance_plot,
    performance_plot,
    best_stats,
    statistik_peserta,

    Args:
        bib_number (int): Nomor BIB peserta.
        df_detail (pd.DataFrame): DataFrame yang berisi detail aktivitas peserta.
        df_podium (pd.DataFrame): DataFrame yang berisi informasi podium peserta.
        data_path (dict): Dictionary yang berisi path untuk menyimpan berbagai output file.
        verbose (bool) : Jika benar, maka proses sukses / gagal akan ditampilkan ke layar
        """
    
    # Implementasi Prosedur      
    def generate_facts_about_you(verbose=True, debug=False, simpan_ke_file=True):
        """
        Menghasilkan fakta-fakta tentang peserta berdasarkan statistik mereka dan membandingkannya dengan peserta lain.

        Args:
            debug (bool, optional): Jika True, cetak informasi debug. Defaults to False.
            simpan_ke_file (bool, optional): Jika True, simpan hasil ke file. Defaults to True.
        """
        try:

            # Fungsi untuk menghitung persentil dalam subset data
            def get_percentiles(df_subset):
                return {
                    "jarak": (df_subset['jarak'] < jarak_km).mean() * 100,
                    "waktu": (df_subset['elapsed_minutes'] < waktu_menit).mean() * 100,
                    "elevasi": (df_subset['elevasi'] < elevasi_m).mean() * 100,
                    "speed": (df_subset['speed'] < speed_kmh).mean() * 100,
                    "workout": (df_subset['workout'] < workout_count).mean() * 100,
                }

            # Perhitungan berdasarkan kelompok berbeda
            overall_stats = get_percentiles(df_statistik)
            gender_stats = get_percentiles(df_statistik[df_statistik['gender'] == gender])
            category_stats = get_percentiles(df_statistik[df_statistik['kategori'] == kategori])
            activity_stats = get_percentiles(df_statistik[df_statistik['jenis_kegiatan'] == jenis_kegiatan])

            # Hitung persentase peserta yang selesai atau tidak
            total_peserta = len(df_statistik)
            jumlah_selesai = (df_statistik['finish'] == 'Ya').sum()
            jumlah_tidak_selesai = total_peserta - jumlah_selesai

            if status_finish == 'Ya':
                persentil_finish = (jumlah_selesai / total_peserta) * 100
                status_text = f"Kamu adalah bagian dari {persentil_finish:.1f}% peserta yang berhasil menyelesaikan event."
            else:
                persentil_not_finish = (jumlah_tidak_selesai / total_peserta) * 100
                status_text = f"Kamu adalah bagian dari {persentil_not_finish:.1f}% peserta yang tidak menyelesaikan event."

            if simpan_ke_file:
                output_file = facts_about_you_path
                with open(output_file, "w") as file:
                    # Tulis status ke file
                    file.write(f"{status_text}\n\n")
                    
                    # Fungsi untuk mencetak hasil dalam berbagai kategori dan menyimpan ke file
                    file.write(f"Kamu menempuh sejauh {jarak_km:.2f} km dan itu lebih jauh dari:\n")
                    file.write(f"{overall_stats['jarak']:.1f}% keseluruhan peserta.\n")
                    file.write(f"{gender_stats['jarak']:.1f}% peserta dengan gender yang sama ({gender}).\n")
                    file.write(f"{category_stats['jarak']:.1f}% peserta dalam kategori yang sama ({kategori}).\n")
                    file.write(f"{activity_stats['jarak']:.1f}% dengan jenis kegiatan yang sama ({jenis_kegiatan})\n\n")

                    file.write(f"Kamu menghabiskan waktu {waktu_menit:.1f} menit dan itu lebih lama dari:\n")
                    file.write(f"{overall_stats['waktu']:.1f}% keseluruhan peserta.\n")
                    file.write(f"{gender_stats['waktu']:.1f}% peserta dengan gender yang sama ({gender}).\n")
                    file.write(f"{category_stats['waktu']:.1f}% peserta dalam kategori yang sama ({kategori}).\n")
                    file.write(f"{activity_stats['waktu']:.1f}% dengan jenis kegiatan yang sama ({jenis_kegiatan})\n\n")

                    file.write(f"Kamu mengumpulkan elevasi {elevasi_m:.1f} m dan itu lebih tinggi dari:\n")
                    file.write(f"{overall_stats['elevasi']:.1f}% keseluruhan peserta.\n")
                    file.write(f"{gender_stats['elevasi']:.1f}% peserta dengan gender yang sama ({gender}).\n")
                    file.write(f"{category_stats['elevasi']:.1f}% peserta dalam kategori yang sama ({kategori}).\n")
                    file.write(f"{activity_stats['elevasi']:.1f}% dengan jenis kegiatan yang sama ({jenis_kegiatan})\n\n")

                    file.write(f"Kamu melaju dengan average speed {speed_kmh:.2f} km/h dan itu lebih cepat dari:\n")
                    file.write(f"{overall_stats['speed']:.1f}% keseluruhan peserta.\n")
                    file.write(f"{gender_stats['speed']:.1f}% peserta dengan gender yang sama ({gender}).\n")
                    file.write(f"{category_stats['speed']:.1f}% peserta dalam kategori yang sama ({kategori}).\n")
                    file.write(f"{activity_stats['speed']:.1f}% dengan jenis kegiatan yang sama ({jenis_kegiatan})\n\n")

                    file.write(f"Kamu melakukan {workout_count} workout dan itu lebih sering dari:\n")
                    file.write(f"{overall_stats['workout']:.1f}% keseluruhan peserta.\n")
                    file.write(f"{gender_stats['workout']:.1f}% peserta dengan gender yang sama ({gender}).\n")
                    file.write(f"{category_stats['workout']:.1f}% peserta dalam kategori yang sama ({kategori}).\n")
                    file.write(f"{activity_stats['workout']:.1f}% dengan jenis kegiatan yang sama ({jenis_kegiatan})\n\n")

                    # Memberi pesan konfirmasi
                    
                    if verbose: print(f"✅ Fakta peserta telah disimpan ke {facts_about_you_path}")
        except Exception as e:
            if verbose:
                print(e)
                print(traceback.format_exc())  # Print the full traceback (line number & error details)
                print("❌ Fakta peserta gagal disimpan")

    def generate_agregate_statistics(verbose=True, debug=False, simpan_ke_file=True):
        """
        Menghasilkan statistik agregat berdasarkan kategori dan jenis kegiatan, serta statistik individu peserta.

        Args:
            debug (bool, optional): Jika True, cetak informasi debug ke terminal. Defaults to False.
            simpan_ke_file (bool, optional): Jika True, simpan hasil ke file. Defaults to True.
        """
        try:  
            # Filter data berdasarkan kategori dan jenis kegiatan dengan .copy()
            df_kategori = df_statistik[df_statistik['kategori'] == kategori].copy()
            df_jenis_kegiatan = df_statistik[df_statistik['jenis_kegiatan'] == jenis_kegiatan].copy()

            # Konversi waktu agar bisa dihitung dalam menit
            df_kategori.loc[:, 'elapsed_minutes'] = pd.to_timedelta(df_kategori['elapsed_time'], errors='coerce').dt.total_seconds() / 60
            df_jenis_kegiatan.loc[:, 'elapsed_minutes'] = pd.to_timedelta(df_jenis_kegiatan['elapsed_time'], errors='coerce').dt.total_seconds() / 60

            # Fungsi untuk menghitung statistik dan menyimpan ke file
            def hitung_statistik(df, label, file):
                stats = {
                    "Max Speed (km/h)": df["speed"].max(),
                    "Min Speed (km/h)": df["speed"].min(),
                    "Average Speed (km/h)": df["speed"].mean(),
                    "Max Elapsed Time (min)": df["elapsed_minutes"].max(),
                    "Min Elapsed Time (min)": df["elapsed_minutes"].min(),
                    "Average Elapsed Time (min)": df["elapsed_minutes"].mean(),
                    "Max Distance (km)": df["jarak"].max(),
                    "Min Distance (km)": df["jarak"].min(),
                    "Average Distance (km)": df["jarak"].mean(),
                    "Max Elevation (m)": df["elevasi"].max(),
                    "Min Elevation (m)": df["elevasi"].min(),
                    "Average Elevation (m)": df["elevasi"].mean(),
                    "Max Workout Count": df["workout"].max(),
                    "Min Workout Count": df["workout"].min(),
                    "Average Workout Count": df["workout"].mean(),
                }

                if simpan_ke_file:
                    # Simpan ke file
                    file.write(f" Statistik {label} \n\n")
                    for key, value in stats.items():
                        file.write(f"{key}: {value:.2f}\n")

            if simpan_ke_file:
                # **Buka file untuk menulis hasil statistik**
                output_file = statistik_semua_path
                with open(output_file, "w") as file:
                    # Hitung statistik untuk semua kategori
                    hitung_statistik(df_statistik, "Keseluruhan Peserta", file)
                    
                    if verbose: print(f"✅ Statistik Agregat Seluruh Peserta telah disimpan ke {statistik_semua_path}")

                output_file = statistik_kategori_path
                with open(output_file, "w") as file:
                    hitung_statistik(df_kategori, f"Kategori {kategori}", file)
                    
                    if verbose: print(f"✅ Statistik Agregat Kategori telah disimpan ke {statistik_kategori_path}")

                output_file = statistik_kegiatan_path
                with open(output_file, "w") as file:
                    hitung_statistik(df_jenis_kegiatan, f"Jenis Kegiatan {jenis_kegiatan}", file)
                    
                    if verbose: print(f"✅ Statistik Agregat jenis kegiatan telah disimpan ke {statistik_kegiatan_path}")

                output_file = statistik_individu_path
                with open(output_file, "w") as file:
                    # Statistik peserta individu
                    file.write(f"===== Statistik Peserta (BIB: {bib_number:04d}) =====\n")
                    file.write(f"Speed: {speed_kmh:.2f} km/h\n")
                    file.write(f"Elapsed Time: {waktu_menit:.2f} menit\n")
                    file.write(f"Distance: {jarak_km:.2f} km\n")
                    file.write(f"Elevation: {elevasi_m:.2f} m\n")
                    file.write(f"Workout Count: {workout_count}\n")
                    
                    if verbose: print(f"✅ Statistik Individu telah disimpan ke {statistik_individu_path}")

            if debug:
                # **Tampilkan juga di terminal**
                if verbose: print(f"\n===== Statistik Peserta (BIB: {bib_number:04d}) =====")
                if verbose: print(f"Speed: {speed_kmh:.2f} km/h")
                if verbose: print(f"Elapsed Time: {waktu_menit:.2f} menit")
                if verbose: print(f"Distance: {jarak_km:.2f} km")
                if verbose: print(f"Elevation: {elevasi_m:.2f} m")
                if verbose: print(f"Workout Count: {workout_count}")

        except Exception as e:
            if verbose:
                print(e)
                print("❌ Statistik peserta gagal disimpan")

    def generate_scatter_speed(verbose=True, debug=False, simpan_ke_file=True):
        """
        Membuat scatter plot antara usia dan kecepatan peserta, dengan highlight untuk peserta tertentu.

        Args:
            debug (bool, optional): Jika True, tampilkan plot dan legend. Defaults to False.
            simpan_ke_file (bool, optional): Jika True, simpan plot ke file. Defaults to True.
        """
        try:
            # Filter out rows where Speed is 0
            df_podium_speed = df_podium[df_podium['speed'] > 0]
            
            # Create a scatter plot, using the 'kategori' column for coloring
            plt.figure(figsize=(8, 6))
            sns.scatterplot(data=df_podium_speed, x='usia', y='speed', hue='kategori', palette='Set1', alpha=0.7)

            # Highlight the participant with BIB = 1
            peserta_podium_speed = df_podium_speed[df_podium_speed['bib_peserta'] == f"{bib_number:04d}"]

            # print(bib_number)
            # print("peserta_podium_speed:")
            # print(peserta_podium_speed)

            # Check the category of the participant with BIB = 1
            jenis_kegiatan = peserta_podium_speed['jenis_kegiatan'].iloc[0]
            category = peserta_podium_speed['kategori'].iloc[0]
            nama_peserta = peserta_podium_speed['nama_individu'].iloc[0]
            speed_highlight = peserta_podium_speed['speed'].iloc[0]

            # Set the color based on the category
            highlight_color = 'red' if jenis_kegiatan == 'Run' else 'blue'

            plt.scatter(peserta_podium_speed['usia'], peserta_podium_speed['speed'], color=highlight_color, s=100, label="Anda", edgecolor='black', marker='*')

            # Add a horizontal line at the Jarak of the highlighted participant
            plt.axhline(y=speed_highlight, color='gray', linestyle='--', alpha=0.5)

            # Add a label for the highlighted value with a bit of vertical offset
            plt.text(peserta_podium_speed['usia'].iloc[0], speed_highlight-2, f'{speed_highlight} km/h', color='black', fontsize=10, ha='center')

            # Set titles and labels
            plt.title(f'Scatter Plot Usia vs Speed Peserta OlympIAE 2025\n nama: {nama_peserta} (BIB = {bib_number:04d})\nKategori : {category}', fontsize=14)
            plt.xlabel('usia', fontsize=12)
            plt.ylabel('Speed (km/h)', fontsize=12)

            if simpan_ke_file:
                # Menyimpan plot
                output_file = scatter_plot_speed_path
                plt.savefig(output_file, dpi=300, bbox_inches='tight')  # Menyimpan dengan batas yang rapat

                if verbose: print(f"✅ Scatter plot usia-speed telah disimpan ke {output_file}")
            if debug:
                # Show legend
                plt.legend()

                # Show the plot
                plt.show()
        except Exception as e:
            print(e)
            print(traceback.format_exc())  # Print the full traceback (line number & error details)
            if verbose: print(f"❌ Scatter plot usia-speed gagal disimpan")
            
    def generate_scatter_distance(verbose=True, debug=False, simpan_ke_file=True):
        """
        Membuat scatter plot antara usia dan jarak peserta, dengan highlight untuk peserta tertentu.

        Args:
            debug (bool, optional): Jika True, tampilkan plot dan legend. Defaults to False.
            simpan_ke_file (bool, optional): Jika True, simpan plot ke file. Defaults to True.
        """
        try:
            # Filter out rows where jarak is 0
            df_podium_jarak = df_podium[df_podium['jarak'] > 0]

            # Create a scatter plot, using the 'kategori' column for coloring
            plt.figure(figsize=(8, 6))
            sns.scatterplot(data=df_podium_jarak, x='usia', y='jarak', hue='kategori', palette='Set1', alpha=0.7)

            # Highlight the participant with BIB = 1
            peserta_podium_jarak = df_podium_jarak[df_podium_jarak['bib_peserta'] == f"{bib_number:04d}"]

            # Check the category of the participant with BIB = 1
            jenis_kegiatan = peserta_podium_jarak['jenis_kegiatan'].iloc[0]
            category = peserta_podium_jarak['kategori'].iloc[0]
            nama_peserta = peserta_podium_jarak['nama_individu'].iloc[0]
            jarak_highlight = peserta_podium_jarak['jarak'].iloc[0]

            # Set the color based on the category
            highlight_color = 'red' if jenis_kegiatan == 'Run' else 'blue'

            plt.scatter(peserta_podium_jarak['usia'], peserta_podium_jarak['jarak'], color=highlight_color, s=100, label="Anda", edgecolor='black', marker='*')

            # Add a horizontal line at the Jarak of the highlighted participant
            plt.axhline(y=jarak_highlight, color='gray', linestyle='--', alpha=0.5)

            # Add a label for the highlighted value with a bit of vertical offset
            plt.text(peserta_podium_jarak['usia'].iloc[0], jarak_highlight-20, f'{jarak_highlight} km', color='black', fontsize=10, ha='center')

            # Set titles and labels
            plt.title(f'Scatter Plot Usia vs jarak Peserta OlympIAE 2025\n nama: {nama_peserta} (BIB = {bib_number:04d})\nKategori : {category}', fontsize=14)
            plt.xlabel('usia', fontsize=12)
            plt.ylabel('jarak (km)', fontsize=12)

            if simpan_ke_file:
                # Menyimpan plot
                output_file = scatter_plot_distance_path
                plt.savefig(output_file, dpi=300, bbox_inches='tight')  # Menyimpan dengan batas yang rapat

                if verbose: print(f"✅ Scatter plot usia-jarak telah disimpan ke {output_file}")

            if debug:
                # Show legend
                plt.legend()

                # Show the plot
                plt.show()
        except Exception as e:
            print(e)
            print(traceback.format_exc())  # Print the full traceback (line number & error details)
            if verbose: print(f"❌ Scatter plot usia-jarak gagal disimpan")

    def generate_scatter_elev_gain(verbose=True, debug=False, simpan_ke_file=True):
        """
        Membuat scatter plot antara usia dan elevasi peserta, dengan highlight untuk peserta tertentu.

        Args:
            debug (bool, optional): Jika True, tampilkan plot dan legend. Defaults to False.
            simpan_ke_file (bool, optional): Jika True, simpan plot ke file. Defaults to True.
        """
        try:
            # Filter out rows where Elevasi is 0
            df_podium_elevasi = df_podium[df_podium['elevasi'] > 0]

            # Create a scatter plot, using the 'kategori' column for coloring
            plt.figure(figsize=(8, 6))
            sns.scatterplot(data=df_podium_elevasi, x='usia', y='elevasi', hue='kategori', palette='Set1', alpha=0.7)

            # Highlight the participant with BIB = 1
            peserta_podium_Elevasi = df_podium_elevasi[df_podium_elevasi['bib_peserta'] == f"{bib_number:04d}"]

            # Check the category of the participant with BIB = 1
            jenis_kegiatan = peserta_podium_Elevasi['jenis_kegiatan'].iloc[0]
            category = peserta_podium_Elevasi['kategori'].iloc[0]
            nama_peserta = peserta_podium_Elevasi['nama_individu'].iloc[0]
            Elevasi_highlight = peserta_podium_Elevasi['elevasi'].iloc[0]

            # Set the color based on the category
            highlight_color = 'red' if jenis_kegiatan == 'Run' else 'blue'

            plt.scatter(peserta_podium_Elevasi['usia'], peserta_podium_Elevasi['elevasi'], color=highlight_color, s=100, label="Anda", edgecolor='black', marker='*')

            # Add a horizontal line at the Elevasi of the highlighted participant
            plt.axhline(y=Elevasi_highlight, color='gray', linestyle='--', alpha=0.5)

            # Add a label for the highlighted value with a bit of vertical offset
            plt.text(peserta_podium_Elevasi['usia'].iloc[0], Elevasi_highlight+20, f'{Elevasi_highlight} m', color='black', fontsize=10, ha='center')

            # Set titles and labels
            plt.title(f'Scatter Plot Usia vs Elevasi Peserta OlympIAE 2025\n nama: {nama_peserta} (BIB = {bib_number:04d})\nKategori : {category}', fontsize=14)
            plt.xlabel('usia', fontsize=12)
            plt.ylabel('Elevasi (m)', fontsize=12)

            if simpan_ke_file:
                # Menyimpan plot
                output_file = scatter_plot_elevation_path
                plt.savefig(output_file, dpi=300, bbox_inches='tight')  # Menyimpan dengan batas yang rapat

                if verbose: print(f"✅ Scatter plot usia-elevation telah disimpan ke {output_file}")

            if debug:
                # Show legend
                plt.legend()

                # Show the plot
                plt.show()
        except Exception as e:
            print(e)
            print(traceback.format_exc())  # Print the full traceback (line number & error details)
            if verbose: print(f"❌ Scatter plot usia-elevation gagal disimpan")

    def generate_scatter_elapsed_time(verbose=True, debug=False, simpan_ke_file=True):
        """
        Membuat scatter plot antara usia dan waktu tempuh (elapsed time) peserta, dengan highlight untuk peserta tertentu.

        Args:
            debug (bool, optional): Jika True, tampilkan plot dan legend. Defaults to False.
            simpan_ke_file (bool, optional): Jika True, simpan plot ke file. Defaults to True.
        """
        try:
            df_podium_elapsed_time = df_podium

            # Convert 'elapsed_time' to total minutes
            df_podium_elapsed_time['elapsed_time'] = pd.to_timedelta(df_podium_elapsed_time['elapsed_time'])
            df_podium_elapsed_time['elapsed_minutes'] = df_podium_elapsed_time['elapsed_time'].dt.total_seconds() / 60  # Convert to minutes

            # Filter elapsed time > 0
            df_podium_elapsed_time = df_podium_elapsed_time[df_podium_elapsed_time['elapsed_minutes'] > 0]

            # Create a scatter plot, using the 'kategori' column for coloring
            plt.figure(figsize=(8, 6))
            sns.scatterplot(data=df_podium_elapsed_time, x='usia', y='elapsed_minutes', hue='kategori', palette='Set1', alpha=0.7)

            # Highlight the participant with BIB = 1
            highlight = df_podium_elapsed_time[df_podium_elapsed_time['bib_peserta'] == f"{bib_number:04d}"]

            # Check the category of the participant with BIB = 1
            jenis_kegiatan = highlight['jenis_kegiatan'].iloc[0]
            category = highlight['kategori'].iloc[0]
            nama_peserta = highlight['nama_individu'].iloc[0]
            elapsed_time_highlight = highlight['elapsed_minutes'].iloc[0]

            # Set the color based on the category
            highlight_color = 'red' if jenis_kegiatan == 'Run' else 'blue'

            # Plot the highlighted participant
            plt.scatter(highlight['usia'], highlight['elapsed_minutes'], color=highlight_color, s=100, label="Anda", edgecolor='black', marker='*')

            # Add a horizontal line at the elapsed_time of the highlighted participant
            plt.axhline(y=elapsed_time_highlight, color='gray', linestyle='--', alpha=0.5)

            # Add a label for the highlighted value with a bit of vertical offset
            plt.text(highlight['usia'].iloc[0], elapsed_time_highlight + 20, f'{elapsed_time_highlight:.1f} min', color='black', fontsize=10, ha='center')

            # Set titles and labels
            plt.title(f'Scatter Plot Usia vs Elapsed Time Peserta OlympIAE 2025\nNama: {nama_peserta} (BIB = {bib_number:04d})\nKategori: {category}', fontsize=14)
            plt.xlabel('usia', fontsize=12)
            plt.ylabel('Elapsed Time (minutes)', fontsize=12)

            if simpan_ke_file:
                # Menyimpan plot
                output_file = scatter_plot_elapsed_time_path
                plt.savefig(output_file, dpi=300, bbox_inches='tight')  # Menyimpan dengan batas yang rapat

                if verbose: print(f"✅ Scatter plot usia-elapsed time telah disimpan ke {output_file}")

            if debug:
                # Show legend
                plt.legend()
                # Show the plot
                plt.show()
        except Exception as e:
            print(e)
            print(traceback.format_exc())  # Print the full traceback (line number & error details)
            if verbose: print(f"❌ Scatter plot usia-elapsed time gagal disimpan")

    def generate_finish_proportion(verbose=True, debug=False, simpan_ke_file=True):
        """
        Menghasilkan bar chart yang menunjukkan proporsi peserta yang menyelesaikan event (finish) dan yang tidak.

        Args:
        debug (bool, opsional): Jika True, tampilkan plot. Default ke False.
        simpan_ke_file (bool, opsional): Jika True, simpan plot ke file. Default ke True.
        """
        try:
            # Hitung jumlah peserta berdasarkan status 'finish'
            finish_counts = df_podium['finish'].value_counts(normalize=True) * 100  # Menghitung persentase

            # Membuat bar chart
            plt.figure(figsize=(6, 4))
            ax = sns.barplot(x=finish_counts.index, y=finish_counts.values, hue=finish_counts.index, palette=['green', 'red'], legend=False)

            # Menambahkan label persentase di dalam bar
            for i, val in enumerate(finish_counts.values):
                plt.text(i, val - 5, f'{val:.1f}%', ha='center', fontsize=20, color='white', fontweight='bold')  # Geser ke dalam dan ubah warna ke putih

            # Menambahkan judul dan label
            plt.title('Proporsi Peserta yang Menyelesaikan Event', fontsize=14)
            plt.xlabel('Finish?', fontsize=12)
            plt.ylabel('Persentase (%)', fontsize=12)

            # Menyesuaikan batas sumbu Y agar label tidak keluar dari bar
            plt.ylim(0, max(finish_counts.values) + 10)

            if simpan_ke_file:
                # Menyimpan plot
                output_file = finish_proportion_path
                plt.savefig(output_file, dpi=300, bbox_inches='tight')  # Menyimpan dengan batas yang rapat
                if verbose: print(f"✅ Grafik proporsi finish telah disimpan ke {output_file}")

            if debug:
                # Menampilkan plot
                plt.show()
        except Exception as e:
            if verbose: print(f"❌ Grafik proporsi finish gagal disimpan. Error: {e}")

    def generate_finish_per_year_histogram(verbose=True, debug=False, simpan_ke_file=True):
        """
         membuat histogram bertumpuk yang menunjukkan distribusi jumlah peserta yang berhasil menyelesaikan event per tahun (angkatan) untuk setiap kategori yang ditentukan.

        Args:
        debug (bool, opsional): Jika True, tampilkan plot. Defaultnya False.
        simpan_ke_file (bool, opsional): Jika True, simpan plot ke file. Defaultnya True.
        """
        try:
            # Daftar kategori yang ingin dimasukkan dalam histogram
            kategori_list = [
                "85K RUN DUO",
                "170K RUN TEAM OF 4",
                "42.2K RUN SOLO",
                "180K RIDE SOLO",
                "540K RIDE TEAM OF 4"
            ]

            # Hitung total peserta di setiap kategori (termasuk yang belum finish)
            total_peserta_per_kategori = {kategori: len(df_podium[df_podium['kategori'] == kategori]) for kategori in kategori_list}

            # Filter hanya peserta yang sudah finish
            df_finish = df_podium[df_podium['finish'] == 'Ya'].copy()

            # Pastikan kolom 'angkatan' hanya berisi angka, abaikan nilai non-numerik
            df_finish = df_finish[pd.to_numeric(df_finish['angkatan'], errors='coerce').notna()]
            df_finish['angkatan'] = df_finish['angkatan'].astype(int)

            # Pastikan semua angkatan muncul di sumbu x
            all_angkatan = np.arange(df_finish['angkatan'].min(), df_finish['angkatan'].max() + 1)

            # Warna untuk setiap kategori
            colors = ["blue", "orange", "green", "red", "purple"]

            # Buat dataframe untuk jumlah peserta per angkatan di setiap kategori
            angkatan_dict = {}
            for kategori in kategori_list:
                angkatan_dict[kategori] = df_finish[df_finish['kategori'] == kategori]['angkatan'].value_counts().sort_index()
                angkatan_dict[kategori] = angkatan_dict[kategori].reindex(all_angkatan, fill_value=0)

            # Buat plot
            plt.figure(figsize=(14, 7))

            bar_width = 0.8  # Lebar bar
            x_positions = np.arange(len(all_angkatan))
            bottom_values = np.zeros(len(all_angkatan))  # Untuk menumpuk bar di atas satu sama lain

            # Plot masing-masing kategori dalam bentuk stacked bar
            bars = []
            for i, kategori in enumerate(kategori_list):
                bars_kategori = plt.bar(x_positions, angkatan_dict[kategori].values, width=bar_width,
                                        color=colors[i], edgecolor='black', label=kategori, bottom=bottom_values)
                bars.append(bars_kategori)
                bottom_values += angkatan_dict[kategori].values  # Tambahkan nilai ke bottom untuk stack berikutnya

            # Tambahkan angka di atas setiap bar (total akumulasi per angkatan)
            for i, x in enumerate(x_positions):
                total_y = bottom_values[i]
                if total_y > 0:
                    plt.text(x, total_y + 0.1, int(total_y), ha='center', va='bottom', fontsize=10)

            # **Perbaikan: Set batas atas sumbu y agar tidak terpotong**
            max_y = max(bottom_values)  # Nilai tertinggi di grafik
            plt.ylim(0, max_y * 1.2)  # Tambahkan margin 10%

            # Hitung persentase peserta yang finish dari total peserta di kategori masing-masing
            persentase_per_kategori = {
                kategori: (len(df_finish[df_finish['kategori'] == kategori]) / total_peserta_per_kategori[kategori]) * 100
                if total_peserta_per_kategori[kategori] > 0 else 0
                for kategori in kategori_list
            }

            # Anotasi persentase di pojok kiri atas
            annotation_text = "\n".join([f"{kategori}: {persentase_per_kategori[kategori]:.1f}% finish" for kategori in kategori_list])
            plt.text(0.02, 0.95, annotation_text, transform=plt.gca().transAxes, fontsize=12,
                    verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

            # Atur label dan judul
            plt.xlabel('angkatan')
            plt.ylabel('Jumlah Peserta')
            plt.title('Distribusi Angkatan yang Sudah Finish (Update 26 Februari 2025)')

            # Atur sumbu x agar menampilkan semua angkatan
            plt.xticks(x_positions, all_angkatan, rotation=45)

            # Tambahkan grid
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            # Tambahkan legenda
            plt.legend()

            if simpan_ke_file:
                # Menyimpan plot
                output_file = finish_per_year_histogram_path
                plt.savefig(output_file, dpi=300, bbox_inches='tight')  # Menyimpan dengan batas yang rapat
                if verbose: print(f"✅ Histogram finish per angkatan telah disimpan ke {output_file}")
            if debug:
                plt.show()
        except Exception as e:
            print(e)
            print(traceback.format_exc())  # Print the full traceback (line number & error details)
            if verbose: print(f"❌ Histogram Finish per Year gagal disimpan")

    def generate_activity_table(verbose=True, debug=False, simpan_ke_file=True):
        """
        Menghasilkan tabel aktivitas peserta yang berisi informasi jarak, pace, dan tanggal lari, dan menyimpannya sebagai gambar PNG.

        Args:
        debug (bool, opsional): Jika True, tampilkan plot. Defaultnya False.
        simpan_ke_file (bool, opsional): Jika True, simpan tabel ke file. Defaultnya True.
        """
        try:
            # Filter berdasarkan 'bib_peserta'
            peserta_summary_detail = df_detail[df_detail["bib_peserta"] == f"{bib_number:04d}"]

            # Reset index dan menambahkan nomor urut baru
            df_tabel_summary = peserta_summary_detail[['jarak', 'pace', 'tanggal_lari']].reset_index(drop=True)
            df_tabel_summary = df_tabel_summary.sort_values(by="tanggal_lari")
            df_tabel_summary["pace"] = df_tabel_summary["pace"].apply(lambda x: f"{x.components.minutes:02}:{x.components.seconds:02}") # pace hanya ditampilkan menit dan detik
            df_tabel_summary.insert(0, 'No', range(1, len(df_tabel_summary) + 1))

            # Ubah nama kolom sesuai permintaan
            df_tabel_summary.rename(columns={'jarak': 'Jarak (km)', 'pace': 'Pace (/km)'}, inplace=True)

            # Membuat figure dan axes
            fig, ax = plt.subplots(figsize=(8, 6))

            # Menghapus axes ticks dan spines
            ax.axis('off')

            # Membuat tabel
            table = ax.table(cellText=df_tabel_summary.values, colLabels=df_tabel_summary.columns, 
                             loc='center', cellLoc='center')

            # Mengatur ukuran font tabel
            table.set_fontsize(10)

            # Mengatur batas cell
            table.scale(1, 1)

            # Mengatur judul tabel dengan padding untuk menghindari tumpang tindih
            nama_individu = peserta_summary_detail["nama_individu"].iloc[0]
            kategori_lomba = peserta_summary_detail["kategori"].iloc[0]
            ax.set_title(f"Tabel Aktivitas OlympIAE 2025\nKategori: {kategori_lomba}\n{nama_individu}\n(No. BIB: {bib_number:04d})", 
                         fontsize=12, fontweight='bold', pad=50)  # Padding agar tidak bertabrakan

            # Mengatur lebar kolom agar menyesuaikan data
            for i, col in enumerate(df_tabel_summary.columns):
                table.auto_set_column_width(col=i)

            # Mengatur header tabel tebal dan background abu-abu
            for (i, key) in enumerate(table._cells):  
                cell = table._cells[key]
                if key[0] == 0:  # Baris pertama (header)
                    cell.set_text_props(fontweight='bold', color='black')  # Teks tebal dan warna hitam
                    cell.set_facecolor('#EEEEEE')  # Warna abu-abu

            # Menyesuaikan tata letak otomatis
            plt.tight_layout()

            # Memberikan ruang ekstra di bagian atas untuk menghindari tumpang tindih judul
            fig.subplots_adjust(top=0.85)

            if simpan_ke_file:
                # Menyimpan tabel dalam format PNG dengan batas ketat agar tidak ada potongan
                output_file = data_summary_path
                plt.savefig(output_file, dpi=300, bbox_inches='tight')  # Menyimpan dengan batas yang optimal
                if verbose: print(f"✅ Tabel aktivitas peserta telah disimpan ke {output_file}")

            if debug:
                # Menampilkan plot (opsional)
                plt.show()
        except Exception as e:
            print(e)
            print(traceback.format_exc())  # Print the full traceback (line number & error details)
            if verbose: print(f"❌ Tabel aktivitas peserta gagal disimpan. Error: {e}")

    def generate_activity_barplot(verbose=True, debug=False, simpan_ke_file=True):
        """
        Menghasilkan bar plot yang menunjukkan jarak tempuh peserta per tanggal lari.

        Args:
        debug (bool, opsional): Jika True, tampilkan plot. Defaultnya False.
        simpan_ke_file (bool, opsional): Jika True, simpan plot ke file. Defaultnya True.
        """
        try:
            peserta_barplot = df_detail[df_detail["bib_peserta"] == f"{bib_number:04d}"].copy()

            # Jika tidak ada data untuk bib_target, lanjutkan ke BiB berikutnya
            if peserta_barplot.empty:
                if verbose: print(f"BIB {bib_number:04d} tidak ditemukan, melewati peserta ini.")
            else:
                # Pastikan kolom 'tanggal_lari' diubah ke tipe datetime
                peserta_barplot["tanggal_lari"] = pd.to_datetime(peserta_barplot["tanggal_lari"], format='%d/%m/%Y %H:%M:%S', errors="coerce")

                # Ambil hanya tanggalnya saja
                peserta_barplot["tanggal"] = peserta_barplot["tanggal_lari"].dt.date
        
                # Hapus baris yang tidak memiliki data tanggal atau jarak
                peserta_barplot = peserta_barplot.dropna(subset=["tanggal", "jarak"])
                # catatan : format harus dd/mm/yy hh:mm:ss. misal : 01/02/2025 06:27:49. 
                # kalau berbeda misalkan 01/02/2025 06:27 , maka error.
        
                # **Gabungkan jarak jika ada aktivitas lebih dari satu pada tanggal yang sama**
                df_grouped = peserta_barplot.groupby("tanggal", as_index=False)["jarak"].sum()

                # Ubah format tanggal menjadi "03-Feb" untuk label sumbu x
                df_grouped["Tanggal Label"] = df_grouped["tanggal"].apply(lambda x: x.strftime('%d-%b'))

                # Ambil nama individu berdasarkan bib_target
                nama_individu = peserta_barplot["nama_individu"].iloc[0]  # Ambil nama individu dari baris pertama yang sesuai

                # Membuat Bar Plot
                plt.figure(figsize=(10, 5))
                bars = plt.bar(df_grouped["Tanggal Label"], df_grouped["jarak"], color='#04149d', label=nama_individu)

                # Menambahkan label di atas setiap batang
                for bar in bars:
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.1f}", 
                                ha='center', va='bottom', fontsize=10, fontweight='bold')

                # Menambahkan label dan judul
                plt.xlabel("Tanggal Lari")
                plt.ylabel("Jarak Tempuh (km)")
                plt.title(f"Bar Plot Jarak Tempuh {nama_individu} (no. BIB : {bib_number:04d})")
                plt.legend()
                plt.grid(True, axis='y', linestyle='--', alpha=0.7)

                # Rotasi sumbu x agar lebih terbaca
                plt.xticks(rotation=45)

                if simpan_ke_file:
                    # Menyimpan plot
                    output_file = distance_time_bar_path
                    plt.savefig(output_file, dpi=300, bbox_inches='tight')  # Menyimpan dengan batas yang rapat
                    if verbose: print(f"✅ Bar plot aktivitas peserta telah disimpan ke {output_file}")

                if debug:
                    # Tampilkan plot
                    plt.show()
        except Exception as e:
            print(e)
            print(traceback.format_exc())  # Print the full traceback (line number & error details)
            if verbose: print(f"❌ Bar plot aktivitas peserta gagal disimpan")

    def generate_cumulative_distance_plot(verbose=True, debug=False, simpan_ke_file=True):
        """
        Menghasilkan plot kurva jarak kumulatif peserta berdasarkan tanggal lari.

        Args:
        debug (bool, opsional): Jika True, tampilkan plot. Defaultnya False.
        simpan_ke_file (bool, opsional): Jika True, simpan plot ke file. Defaultnya True.
        """
        try:
            # Buat salinan data peserta berdasarkan BIB
            peserta_kumulatif = df_detail[df_detail["bib_peserta"] == f"{bib_number:04d}"].copy()

            # Jika tidak ada data untuk bib_number, lanjutkan ke BIB berikutnya
            if peserta_kumulatif.empty:
                if verbose: print(f"BIB {bib_number:04d} tidak ditemukan, melewati peserta ini.")
            else:
                # Pastikan kolom 'tanggal_lari' dalam format datetime
                peserta_kumulatif["tanggal_lari"] = pd.to_datetime(
                    peserta_kumulatif["tanggal_lari"], format='%d/%m/%Y %H:%M:%S', errors="coerce"
                )

                # Ambil hanya tanggalnya saja
                peserta_kumulatif["tanggal"] = peserta_kumulatif["tanggal_lari"].dt.date

                # Hapus baris tanpa tanggal atau jarak
                peserta_kumulatif = peserta_kumulatif.dropna(subset=["tanggal", "jarak"])

                # **Gabungkan jarak jika ada aktivitas lebih dari satu pada tanggal yang sama**
                df_grouped = peserta_kumulatif.groupby("tanggal", as_index=False)["jarak"].sum()

                # **Buat rentang tanggal tetap (1 - 28 Februari)**
                tanggal_range = pd.date_range(start="2025-02-01", end="2025-02-28").date
                df_full = pd.DataFrame({"tanggal": tanggal_range})

                # **Gabungkan data agar hari tanpa aktivitas tetap ada**
                df_full = df_full.merge(df_grouped, on="tanggal", how="left").fillna(0)

                # **Hitung jarak kumulatif**
                df_full["Jarak Kumulatif"] = df_full["jarak"].cumsum()

                # Ubah format tanggal untuk label sumbu x
                df_full["Tanggal Label"] = [t.strftime('%d-%b') for t in df_full["tanggal"]]

                # Ambil nama individu
                nama_individu = peserta_kumulatif["nama_individu"].iloc[0]

                # **Plot Kurva Jarak Kumulatif**
                plt.figure(figsize=(10, 5))
                plt.plot(df_full["tanggal"], df_full["Jarak Kumulatif"], marker='o', linestyle='-', color='#04149d', label=nama_individu)

                # Tambahkan label titik
                for i, txt in enumerate(df_full["Jarak Kumulatif"]):
                    if i % 2 == 0:  # Menampilkan label setiap 2 hari agar lebih rapi
                        plt.text(df_full["tanggal"][i], txt, f"{txt:.1f}", ha='center', va='bottom', fontsize=9)

                # Menambahkan label dan judul
                plt.xlabel("tanggal")
                plt.ylabel("Jarak Kumulatif (km)")
                plt.title(f"Kurva Jarak Kumulatif {nama_individu} (BIB: {bib_number:04d})")
                plt.xticks(df_full["tanggal"], df_full["Tanggal Label"], rotation=45)
                plt.legend()
                plt.grid(True, linestyle='--', alpha=0.7)

                if simpan_ke_file:
                    # Menyimpan plot
                    output_file = cumulative_distance_plot_path
                    plt.savefig(output_file, dpi=300, bbox_inches='tight')  # Menyimpan dengan batas yang rapat
                    if verbose: print(f"✅ Cumulative distance plot telah disimpan ke {output_file}")

                if debug:
                    # Tampilkan plot
                    plt.show()
        except Exception as e:
            print(e)
            print(traceback.format_exc())  # Print the full traceback (line number & error details)
            if verbose: print(f"❌ Cumulative distance plot gagal disimpan")

    def generate_performance_plot(verbose=True, debug=False, simpan_ke_file=True):
        """
        Menghasilkan scatter plot yang menunjukkan hubungan antara kecepatan dan detak jantung rata-rata peserta, dengan ukuran titik yang mewakili jarak tempuh.

        Args:
        debug (bool, opsional): Jika True, tampilkan plot. Defaultnya False.
        simpan_ke_file (bool, opsional): Jika True, simpan plot ke file. Defaultnya True.
        """
        try:
            peserta_detail =  df_detail[df_detail["bib_peserta"] == f"{bib_number:04d}"]

            # Hitung centroid berbobot berdasarkan 'jarak'
            centroid_speed = np.average(peserta_detail["speed"], weights=peserta_detail["jarak"])
            centroid_hr = np.average(peserta_detail["average_heartrate"], weights=peserta_detail["jarak"])

            # Plot scatter plot Average HeartRate vs Speed
            plt.figure(figsize=(8, 6))

            # Membuat scatter plot dengan ukuran titik berdasarkan 'jarak'
            scatter = sns.scatterplot(
                data=peserta_detail, 
                x="speed", 
                y="average_heartrate", 
                size="jarak",  # Ukuran titik berdasarkan Jarak
                sizes=(20, 200),  # Rentang ukuran titik (bisa disesuaikan)
                hue="jarak",  # Warna juga bisa mengikuti Jarak
                palette="coolwarm", 
                edgecolor="black"
            )

            # Tambahkan label untuk setiap titik
            for index, row in peserta_detail.iterrows():
                plt.text(row["speed"], row["average_heartrate"], 
                        f"({row['speed']:.1f}, {row['average_heartrate']:.1f})", 
                        fontsize=9, verticalalignment="bottom", horizontalalignment="right", color="black")

            # Tambahkan titik centroid berbobot
            plt.scatter(centroid_speed, centroid_hr, color="black", s=250, marker="X", edgecolor="white", label="Centroid")

            # Tambahkan label untuk centroid
            plt.text(centroid_speed, centroid_hr, 
                    f"({centroid_speed:.1f}, {centroid_hr:.1f})", 
                    fontsize=10, fontweight="bold", verticalalignment="bottom", horizontalalignment="right", color="black")

            # Tambahkan judul dan label
            nama_individu = peserta_detail["nama_individu"].iloc[0]
            plt.title(f'Scatter Plot Average HR vs Speed\nnama peserta: {nama_individu}\n(no. BIB: {bib_number:04d})', fontsize=14)
            plt.xlabel('Speed (km/h)', fontsize=12)
            plt.ylabel('Average HeartRate (bpm)', fontsize=12)

            # Tampilkan grid untuk memperjelas data
            plt.grid(True, linestyle="--", alpha=0.7)

            # Tampilkan legend untuk ukuran titik dan centroid
            plt.legend(title="Jarak (km)", loc="upper left", bbox_to_anchor=(1, 1))

            if simpan_ke_file:
                # Menyimpan plot
                output_file = performance_plot_path
                plt.savefig(output_file, dpi=300, bbox_inches='tight')  # Menyimpan dengan batas yang rapat
                if verbose: print(f"✅ Performance plot telah disimpan ke {output_file}")

            if debug:
                # Tampilkan plot
                plt.show()
        except Exception as e:
            print(e)
            print(traceback.format_exc())  # Print the full traceback (line number & error details)
            if verbose: print(f"❌ Performance plot gagal disimpan")

    def generate_best_stats(verbose=True, debug=False, simpan_ke_file=True):
        """
        Mengambil statistik aktivitas terbaik dari seorang peserta berdasarkan jenis kegiatan dan target jarak, kemudian mencetak atau menyimpan informasi tersebut ke file.

        Args:
        debug (bool, opsional): Jika True, cetak statistik ke konsol. Defaultnya False.
        simpan_ke_file (bool, opsional): Jika True, simpan statistik ke file. Defaultnya True.
        """
        try:
            # Dapatkan aktivitas terbaik
            if jenis_kegiatan == 'Ride':
                target_distance=180
            elif jenis_kegiatan == 'Run':
                target_distance=42.2
            else:
                return # error
            best_activity_stats = get_best_activity_stats(bib_number, df_detail,target_distance=target_distance)

            # Cek jika ada error
            if "error" in best_activity_stats:
                print(best_activity_stats["error"])
                return

            # Konversi selected_activities menjadi DataFrame
            df_selected = pd.DataFrame(best_activity_stats['Selected Activities'])

            # Tambahkan nomor urut (1, 2, 3, ...)
            df_selected.insert(0, "No.", range(1, len(df_selected) + 1))

            # Format kolom untuk tampilan lebih rapi
            df_selected["elapsed_time"] = df_selected["elapsed_time"].dt.components.apply(
                lambda x: f"{int(x.hours):02}:{int(x.minutes):02}:{int(x.seconds):02}", axis=1
            )

            # Rename kolom untuk tampilan lebih jelas
            df_selected = df_selected.rename(columns={
                "jarak": "Jarak (km)",
                "speed": "Speed (km/h)"
            })

            estimated_time = best_activity_stats["estimated_time_for_target_distance"]
            formatted_time = f"{estimated_time.components.hours:02}:{estimated_time.components.minutes:02}:{estimated_time.components.seconds:02}"

            # Cetak hasil
            if debug:
                 # Cetak tabel aktivitas terbaik
                print("\n📋 Aktivitas Terbaik yang Dipilih:")
                print(df_selected[["No.", "tanggal_lari", "Jarak (km)", "elapsed_time", "Speed (km/h)"]].to_string(index=False)) 

                if verbose: print(f"\n📊 Statistik Aktivitas Terbaik {nama_peserta} (no. BIB: {bib_number:04d})")
                if verbose: print(f"🔹 Total Jarak: {best_activity_stats['Total Distance']:.2f} km")
                if verbose: print(f"🔹 Rata-rata Speed: {best_activity_stats['Average Speed']:.2f} km/h")
                if verbose: print(f"🔹 Total Waktu: {best_activity_stats['Total Time']}")
                if verbose: 
                    print(f"🔹 Estimasi Waktu untuk {target_distance} km: {formatted_time}")


            if simpan_ke_file:
                output_file = best_stat_path
                with open(output_file, "w") as file:
                    file.write("Your Activities for Podium\n") # title
                    file.write("Aktivitas Terbaik yang Dipilih:\n")
                    file.write(df_selected[["No.", "tanggal_lari", "Jarak (km)", "elapsed_time", "Speed (km/h)"]].to_string(index=False)) 
                    file.write(f"\n\nStatistik Aktivitas Terbaik {nama_peserta} (no. BIB :{bib_number:04d})\n")
                    file.write(f"- Total Jarak: {best_activity_stats['Total Distance']:.2f} km\n")
                    file.write(f"- Rata-rata Speed: {best_activity_stats['Average Speed']:.2f} km/h\n")
                    file.write(f"- Total Waktu: {best_activity_stats['Total Time']}\n")

                    file.write(f"- Estimasi Waktu untuk {target_distance} km: {formatted_time}\n")

                    if verbose: print(f"✅ Best Activities telah disimpan ke {output_file}")
        except Exception as e:
            print(e)
            print(traceback.format_exc())  # Print the full traceback (line number & error details)
            if verbose: print(f"❌ Best Activities gagal disimpan")

    # mendapatkan data peserta
    nama_peserta, df_statistik, jarak_km, waktu_menit, elevasi_m, speed_kmh, workout_count, gender, kategori, jenis_kegiatan, status_finish = get_statistik_peserta(f"{bib_number:04d}", df_podium)
    # nama_peserta, df_statistik, jarak_km, waktu_menit, elevasi_m, speed_kmh, workout_count, gender, kategori, jenis_kegiatan, status_finish = get_statistik_peserta(bib_number, df_podium)
    
    # loading path data
    cumulative_distance_plot_path = data_path["cumulative_distance.png"]
    data_summary_path = data_path["data_summary.png"]
    distance_time_bar_path = data_path["distance_time.png"]
    finish_proportion_path = data_path["finish_proportion.png"]
    finish_per_year_histogram_path = data_path["finish_year_histogram.png"]
    performance_plot_path = data_path["performance_plot.png"]
    scatter_plot_distance_path = data_path["scatter_distance.png"]
    scatter_plot_speed_path = data_path["scatter_speed.png"]
    scatter_plot_elevation_path = data_path["scatter_elevation.png"]
    scatter_plot_elapsed_time_path = data_path["scatter_elapsed_time.png"]
    statistik_individu_path = data_path["statistik_individu.txt"]
    statistik_semua_path = data_path["statistik_semua.txt"]
    statistik_kategori_path = data_path["statistik_kategori.txt"]
    statistik_kegiatan_path = data_path["statistik_jenis_kegiatan.txt"]
    best_stat_path = data_path["statistik_terbaik_individu.txt"]
    facts_about_you_path = data_path["facts_about_you.txt"]

    # Jika folder output belum ada, maka buat
    folder_path = f"./output/{bib_number:04d}_{nama_peserta}/data"
    os.makedirs(folder_path, exist_ok=True)

    # Pemanggilan Prosedur 
    generate_facts_about_you(verbose=verbose) # ✅
    generate_agregate_statistics(verbose=verbose) # ✅
    generate_scatter_speed(verbose=verbose) # ✅
    generate_scatter_distance(verbose=verbose) # ✅
    generate_scatter_elev_gain(verbose=verbose) # ✅
    generate_scatter_elapsed_time(verbose=verbose) # ✅
    generate_finish_proportion(verbose=verbose) # ✅
    generate_finish_per_year_histogram(verbose=verbose) # ✅
    generate_activity_table(verbose=verbose) # ✅
    generate_activity_barplot(verbose=verbose) # ✅
    generate_cumulative_distance_plot(verbose=verbose) # ✅
    generate_performance_plot(verbose=verbose) # ✅
    generate_best_stats(verbose=verbose) # ✅
