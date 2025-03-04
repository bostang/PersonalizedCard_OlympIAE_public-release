# IMPORT LIBRARY
from sqlalchemy import create_engine
import pandas as pd
import os
import platform

# VARIABEL GLOBAL
# num_participants = 313 # TOTAL PESERTA
num_participants = 99999 # TOTAL PESERTA

input_file_path = "./input/input_data.xlsx"

# MODE UNTUK CREATE/SEND
CREATE_MODE = 0
SEND_MODE = 1
CREATE_AND_SEND_MODE = 2

# MODE UNTUK AKSI USER
CREATE_AND_SEND_SINGLE_PARTICIPANT_MODE = 1
CREATE_AND_SEND_MULTIPLE_PARTICIPANTS_MODE = 2
CREATE_SINGLE_PARTICIPANT_MODE = 3
CREATE_MULTIPLE_PARTICIPANTS_MODE = 4
SEND_SINGLE_PARTICIPANT_MODE = 5
SEND_MULTIPLE_PARTICIPANTS_MODE = 6
CLEAR_ALL_OUTPUT_MODE = 8
REFRESH_MODE = 9
EXIT_MODE = 0

mode_descriptions = {
    CREATE_AND_SEND_SINGLE_PARTICIPANT_MODE: "Buat dan kirim ke satu orang",
    CREATE_AND_SEND_MULTIPLE_PARTICIPANTS_MODE: "Buat dan Kirim ke banyak orang (range)",
    CREATE_SINGLE_PARTICIPANT_MODE : "Buat untuk satu orang",
    CREATE_MULTIPLE_PARTICIPANTS_MODE : "Buat untuk banyak orang",
    SEND_SINGLE_PARTICIPANT_MODE : "Kirim untuk satu orang",
    SEND_MULTIPLE_PARTICIPANTS_MODE : "Kirim ke banyak orang",
    CLEAR_ALL_OUTPUT_MODE: "CLEAR OUTPUT FOLDER",
    REFRESH_MODE: "REFRESH DISPLAY",
    EXIT_MODE: "EXIT"
}


# ART
olympIAE_start_ASCII =r"""
   ___  _                 ___   _   ___ 
  / _ \| |_  _ _ __  _ __|_ _| /_\ | __|
 | (_) | | || | '  \| '_ \| | / _ \| _| 
  \___/|_|\_, |_|_|_| .__/___/_/ \_\___|
          |__/      |_|          
          personalized card.       
"""

# IMPLEMENTASI FUNGSI/PROSEDUR
def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def input_validate(message=""):
    input_mode_valid_flag = False
    while input_mode_valid_flag == False:
        try:
            var = int(input(message))
        except:
            print("❌ input tidak valid")
        else: # ketika input sudah valid (bukan karakter)
            return var

def load_database(dbname, user, password, host, port):
    # Create SQLAlchemy engine
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")

    # Load data into DataFrames
    df_detail = pd.read_sql("SELECT * FROM detail_activities;", engine)
    df_podium = pd.read_sql("SELECT * FROM podium;", engine)

    return df_detail, df_podium

def load_database_excel(file_path):
    # Database loading
    
    df_detail = pd.read_excel(file_path, sheet_name="Detail Activity", engine="openpyxl")
    df_podium = pd.read_excel(file_path, sheet_name="Podium", engine="openpyxl", converters={'Telp': str})

    return df_detail, df_podium

def get_valid_positive_integer(upper_limit, message=""):
    while True:
        try:
            user_input = int(input(message))
            if 1 <= user_input <= upper_limit:
                return user_input  # Valid input
            else:
                print(f"Error: Masukkan bilangan bulat positif antara 1 dan {upper_limit}.")
        except ValueError:
            print(f"Error: Masukkan bilangan bulat positif antara 1 dan {upper_limit}.")

# def get_valid_positive_integer(upper_limit, message=""): # to return string
#     while True:
#         try:
#             user_input = int(input(message))
#             if 1 <= user_input <= upper_limit:
#                 return f"{user_input:04d}"  # Convert to string with 5-digit zero-padding
#             else:
#                 print(f"Error: Masukkan bilangan bulat positif antara 1 dan {upper_limit}.")
#         except ValueError:
#             print(f"Error: Masukkan bilangan bulat positif antara 1 dan {upper_limit}.")



def get_statistik_peserta(bib_number, df_podium):
    # Filter data berdasarkan kategori dan jenis kegiatan dengan .copy()
    df_statistik = df_podium

    # Pastikan kolom numerik diubah ke tipe data yang benar
    df_statistik['jarak'] = pd.to_numeric(df_statistik['jarak'], errors='coerce')
    df_statistik['elapsed_time'] = pd.to_timedelta(df_statistik['elapsed_time'])
    df_statistik['elapsed_minutes'] = df_statistik['elapsed_time'].dt.total_seconds() / 60  # Convert to minutes
    df_statistik['elevasi'] = pd.to_numeric(df_statistik['elevasi'], errors='coerce')
    df_statistik['speed'] = pd.to_numeric(df_statistik['speed'], errors='coerce')
    df_statistik['workout'] = pd.to_numeric(df_statistik['workout'], errors='coerce')

    # Tentukan peserta yang ingin dibandingkan
    peserta_statistik = df_statistik[df_statistik['bib_peserta'] == bib_number]

    # Buka file untuk menyimpan hasil
    if not peserta_statistik.empty:
        # Ambil data peserta dengan BIB tertentu
        
        nama_peserta = peserta_statistik['nama_individu'].iloc[0]
        jarak_km = peserta_statistik['jarak'].iloc[0]
        waktu_menit = peserta_statistik['elapsed_minutes'].iloc[0]
        elevasi_m = peserta_statistik['elevasi'].iloc[0]
        speed_kmh = peserta_statistik['speed'].iloc[0]
        workout_count = peserta_statistik['workout'].iloc[0]
        gender = peserta_statistik['gender'].iloc[0]
        kategori = peserta_statistik['kategori'].iloc[0]
        jenis_kegiatan = peserta_statistik['jenis_kegiatan'].iloc[0]
        status_finish = peserta_statistik['finish'].iloc[0]

        return nama_peserta, df_statistik, jarak_km, waktu_menit, elevasi_m, speed_kmh, workout_count, gender, kategori, jenis_kegiatan, status_finish

    else: # jika peserta dengan no. bib tertentu tidak ditemukan
        return None, None, None, None, None, None, None, None, None, None, None

def load_data_path(bib_number, df_podium):
    nama_peserta, *_ = get_statistik_peserta(f"{bib_number:04d}", df_podium)
    
    base_path = f"./output/{bib_number:04d}_{nama_peserta}/data"
    
    file_names = [
        "cumulative_distance.png",
        "data_summary.png",
        "distance_time.png",
        "finish_proportion.png",
        "finish_year_histogram.png",
        "performance_plot.png",
        "scatter_distance.png",
        "scatter_speed.png",
        "scatter_elevation.png",
        "scatter_elapsed_time.png",
        "statistik_individu.txt",
        "statistik_semua.txt",
        "statistik_kategori.txt",
        "statistik_jenis_kegiatan.txt",
        "statistik_terbaik_individu.txt",
        "facts_about_you.txt",
    ]

    paths = {name: f"{base_path}/{bib_number:04d}_{name}" for name in file_names}
    
    return paths
