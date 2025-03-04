import shutil
import os

from common import *

def cleanup_all_files_output_folder():
    """ Membersihkan seluruh file dalam folder output tanpa menghapus foldernya """
    flag_input_valid = False
    while not flag_input_valid:
        confirm = input("Apakah yakin untuk membersihkan folder? [n,Y] ")
        if confirm == "Y":
            flag_input_valid = True
            folder_path = "./output/"

            if os.path.exists(folder_path):
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    if os.path.isfile(file_path):  # Hanya hapus file, bukan subfolder
                        os.remove(file_path)

                print(f"✅ Semua file dalam {folder_path} telah dihapus.")
            else:
                print(f"❌ Folder {folder_path} tidak ditemukan.")
        elif confirm == "n":
            flag_input_valid = True
            print(f"Folder output tidak jadi dibersihkan.")
        else:
            print("❌ Input aksi tidak valid. Masukkan [n/Y]")
    
def cleanup_output_folder(bib_number, nama_peserta, verbose=True):
    """ Menghapus folder sementara untuk user dengan no. BIB tertentu (dipanggil setelah file Zip dibentuk)"""
    folder_path = f"./output/{bib_number:04d}_{nama_peserta}"

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        if verbose: print(f"✅ Folder sementara untuk {bib_number:04d}_{nama_peserta} telah dibersihkan.")
    # else:
    #     print("Folder not found!")


def generate_zip(bib_number, nama_peserta, verbose=True):
    """
    Membuat file ZIP dari folder yang berisi data peserta dan kemudian menghapus folder aslinya.

    Args:
        bib_number (int): Nomor BIB peserta.
        nama_peserta (str): Nama lengkap peserta.
    """
    try:
        # Folder you want to zip
        folder_path = f"./output/{bib_number:04d}_{nama_peserta}"

        # Output zip file (without .zip extension)
        output_zip = f"./output/{bib_number:04d}_{nama_peserta}"

        # Create a ZIP archive
        shutil.make_archive(output_zip, 'zip', folder_path)

        cleanup_output_folder(bib_number,nama_peserta, verbose=verbose)
        if verbose: print(f"✅ Proses generate file .zip untuk {bib_number:04d}_{nama_peserta} berhasil.")
    except:
        if verbose: print(f"❌ Proses generate zip gagal")
