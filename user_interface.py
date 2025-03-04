# Library import
from generate_data import *
from generate_card import generate_personalized_card
from generate_zip import generate_zip, cleanup_all_files_output_folder
from send_to_Whatsapp import send_file_whatsapp
from time import sleep
import traceback

from common import *

# IMPLEMENTASI FUNGSI/PROSEDUR

def generate_and_send_single_personalized_card(bib_number, data_path, df_detail, df_podium, verbose=True, mode=CREATE_AND_SEND_MODE):
    """
    mengotomatiskan pembuatan kartu personalisasi untuk satu peserta, termasuk pengumpulan data, pembuatan presentasi, kompresi file, dan pengiriman melalui WhatsApp.

    Args:
        bib_number (int): Nomor BIB peserta.
        data_path (dict): Dictionary yang berisi path ke berbagai file grafik dan statistik.
    """
    try:
        print(f".................... Starting process for no. BIB: {bib_number:04d}....................")
        flag_peserta_ada = False
        if mode == CREATE_MODE or mode == CREATE_AND_SEND_MODE:
            # Gettings stats of the participant
            nama_peserta, *_ = get_statistik_peserta(f"{bib_number:04d}", df_podium)
            
            if nama_peserta != None: # Jika peserta ada di database
                flag_peserta_ada = True # menandai ada peserta

                # Process # 1 : generate data
                generate_complete_data(bib_number=bib_number,df_detail=df_detail,df_podium=df_podium, data_path=data_path,verbose=verbose)

                # Process # 2 : generate PPT->PDF
                generate_personalized_card(bib_number=bib_number, nama_peserta=nama_peserta, data_path=data_path,verbose=verbose)

                # Process # 3 : generate ke ZIP dan bersihkan folder
                generate_zip(bib_number=bib_number, nama_peserta=nama_peserta,verbose=verbose)
            else:
                print(f"❌ Peserta dengan no. BIB {bib_number} tidak ditemukan.")
        if mode == SEND_MODE or mode == CREATE_AND_SEND_MODE:
            # Process # 4 : send to Whatsapp
            flag_peserta_ada = send_file_whatsapp(bib_number=bib_number,verbose=verbose) # kalau sukses, akan di-return True


        if mode == CREATE_AND_SEND_MODE and flag_peserta_ada:
            if verbose: print(f"✅ Proses pembuatan & pengiriman personalized card (no. BIB : {int(bib_number):04d}) berhasil.")
        elif mode == CREATE_MODE and flag_peserta_ada:
            if verbose: print(f"✅ Proses pembuatan personalized card (no. BIB : {int(bib_number):04d}) berhasil.")
        elif mode == SEND_MODE and flag_peserta_ada:
            if verbose: print(f"✅ Proses pengiriman personalized card (no. BIB : {int(bib_number):04d}) berhasil.")

    except Exception as e:
        print(e)
        print(traceback.format_exc())  # Print the full traceback (line number & error details)
        if verbose: print(f"❌ Proses Pembuatan & Pengiriman personalized card (no. BIB : {int(bib_number):04d}) gagal.")
    finally:
        print("............................................................................")

def starting_app(): 
    # clearing the screen
    clear()

    # displaying logo and options
    print_logo_options()

def print_logo_options():
    # printing the starting logo
    print(olympIAE_start_ASCII)

    # printing the option
    for mode, description in mode_descriptions.items():
        print(f"{mode}. {description}")

def process_card_creation_or_sending(df_detail, df_podium, mode, verbose=True):
    """ Fungsi generik untuk membuat/mengirim kartu personalisasi """
    if mode in [CREATE_AND_SEND_MODE, CREATE_MODE, SEND_MODE]:
        action = "Membuat dan mengirim" if mode == CREATE_AND_SEND_MODE else \
                 "Membuat" if mode == CREATE_MODE else "Mengirim"
        if verbose:
            print(f"{action} untuk satu orang")

        bib_number = get_valid_positive_integer(upper_limit=num_participants, message="Masukkan no. BIB:\n>>> ")
        data_path = load_data_path(int(bib_number), df_podium)

        if data_path is None:
            print(f"Skipping BIB {bib_number}, data tidak ditemukan.")
            return  # Skip peserta yang tidak ditemukan
        
        generate_and_send_single_personalized_card(
            bib_number=bib_number, 
            data_path=data_path, 
            df_detail=df_detail, 
            df_podium=df_podium, 
            verbose=verbose, 
            mode=mode
        )

def exit_normally():
    print("👋Good Bye!")
    sleep(1)
    clear()
    exit()

def process_multiple_cards(df_detail, df_podium, mode, verbose=True):
    """ Fungsi generik untuk membuat/mengirim beberapa kartu sekaligus """
    if verbose:
        print("Memproses beberapa orang")
    
    bib_start = get_valid_positive_integer(upper_limit=num_participants, message="Masukkan BIB start:\n>>> ")
    bib_finish = get_valid_positive_integer(upper_limit=num_participants, message="Masukkan BIB finish:\n>>> ")

    for bib_number in range(bib_start, bib_finish + 1):
        data_path = load_data_path(bib_number, df_podium)
        generate_and_send_single_personalized_card(
            bib_number=bib_number, 
            data_path=data_path, 
            df_detail=df_detail, 
            df_podium=df_podium, 
            verbose=verbose, 
            mode=mode
        )

def generate_race_result(df_detail, df_podium, verbose=True):
    # Menyimpan data hasil lomba peserta (solo)
    save_participant_data_to_csv(df_detail, df_podium)

    # Menyimpan data hasil lomba peserta (duo & tim)
    save_all_teams_stats_to_csv(df_detail)

def get_mode_action(df_detail, df_podium, verbose):
    """ Dictionary mapping untuk memetakan mode ke fungsi yang sesuai """
    return {
        CREATE_AND_SEND_SINGLE_PARTICIPANT_MODE: lambda: process_card_creation_or_sending(df_detail, df_podium, CREATE_AND_SEND_MODE, verbose),
        CREATE_AND_SEND_MULTIPLE_PARTICIPANTS_MODE: lambda: process_multiple_cards(df_detail, df_podium, CREATE_AND_SEND_MODE, verbose),
        CREATE_SINGLE_PARTICIPANT_MODE: lambda: process_card_creation_or_sending(df_detail, df_podium, CREATE_MODE, verbose),
        CREATE_MULTIPLE_PARTICIPANTS_MODE: lambda: process_multiple_cards(df_detail, df_podium, CREATE_MODE, verbose),
        SEND_SINGLE_PARTICIPANT_MODE: lambda: process_card_creation_or_sending(df_detail, df_podium, SEND_MODE, verbose),
        SEND_MULTIPLE_PARTICIPANTS_MODE: lambda: process_multiple_cards(df_detail, df_podium, SEND_MODE, verbose),
        GENERATE_RACE_RESULT_MODE : lambda : generate_race_result(df_detail, df_podium, verbose),
        CLEAR_ALL_OUTPUT_MODE: lambda: cleanup_all_files_output_folder(),
        REFRESH_MODE: lambda: (clear(), print_logo_options()),
        EXIT_MODE: lambda: exit_normally(),  
    }
