# Library import
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time

from common import *
from user_interface import * 

# Ubah Konfigurasi Database / bisa juga input dari user
DB_NAME = "olympiae2025"
USER_NAME = "postgres"
PASSWORD = "xxxxxx"
# HOST_NAME = "localhost"
MY_DROPLET_DIGITAL_OCEAN_IPV4 = "xxx.xx.xxx.xxx" # GANTI DENGAN IPV4 server-mu
HOST_NAME = MY_DROPLET_DIGITAL_OCEAN_IPV4
PORT = "5432"

# Main Process
def main(verbose=True):
    """
    Titik masuk utama dari program. Fungsi ini memungkinkan pengguna untuk memilih antara membuat kartu personalisasi untuk satu peserta atau banyak peserta,
    dan kemudian memanggil fungsi generate_single_personalized_card untuk setiap peserta yang dipilih.
    """    

    flag_database_pw_correct = True    

    # Data path loading
    print("loading database..")
    try:
        PASSWORD = input("Masukkan password:\n>>> ")
        df_detail, df_podium = load_database(
            dbname=DB_NAME,
            user=USER_NAME,
            password=PASSWORD,
            host=HOST_NAME,
            port=PORT
        )
    except Exception as e:
        print(e)
        print("❌Gagal terhubung ke database")
        flag_database_pw_correct = False
    finally:
        if flag_database_pw_correct:
            # menampilkan logo awal dan opsi menu
            starting_app()

            while True:
                # menerima input mode sampai valid
                mode = input_validate(f"Action: ({REFRESH_MODE}: REFRESH)\n>>> ")

                # menentukan aksi berdasarkan input mode
                mode_action = get_mode_action(df_detail, df_podium, verbose).get(mode, lambda: print("❌ input tidak valid"))
                mode_action()  # Menjalankan fungsi yang sesuai
            

if __name__ == "__main__":
    main(verbose=True) # ⬅️ atur variabel verbose di sini untuk mengubah tampilan terminal saat program dijalankan
