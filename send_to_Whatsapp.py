import pyautogui
import time
import pandas as pd

# catatan : WA dalam full tab, ukuran layar 1280x720
# Koordinat tombol-tombol
new_chat_xy = [356,67]
number_pad_xy = [624,171]
close_number_pad_country_xy = [619,214]
chat_xy = [497,322]
chat_prompt_xy = [579,694]

typing_delay = 0.02 #sekon
sleep_interval = 0.7 #sekon
long_sleep_duration = 3 #sekon

def escape():
    pyautogui.press('esc')
    time.sleep(sleep_interval)
    pyautogui.press('esc')

def clear_prompt():
    pyautogui.hotkey('ctrl', 'a') # select all
    pyautogui.press('backspace')

def moving(phone_number):
    """
    mengotomatiskan pencarian dan pembukaan obrolan di WhatsApp dengan menggunakan pyautogui untuk mengontrol mouse dan keyboard. Fungsi ini mengasumsikan koordinat mouse dan keyboard tertentu sesuai dengan tata letak WhatsApp.

    Args:
        phone_number (str): Nomor telepon yang akan dicari di WhatsApp Web.
    """
    # New Chat
    pyautogui.hotkey('ctrl', 'n')
    time.sleep(sleep_interval) # delay 1 detik (responsiveness)

    # Pindah ke tombol number pad
    pyautogui.moveTo(number_pad_xy[0],number_pad_xy[1])
    pyautogui.click()          # Click the mouse.

    time.sleep(sleep_interval) # delay 1 detik (responsiveness)

    # Tekan close country pada number pad (untuk manual ketik +62, berlaku untuk selain +62)
    pyautogui.moveTo(close_number_pad_country_xy[0],close_number_pad_country_xy[1])
    pyautogui.click()          # Click the mouse.

    clear_prompt() # mengosongkan prompt nomor telepon (apabila sebelumnya error)

    # mengetik Nomor telepon (mencari)
    pyautogui.write(phone_number, interval=0)  # type with quarter-second pause in between each key

    time.sleep(long_sleep_duration) # delay 5 detik (menunggu sampai phone number found)

    # Tekan tombol chat
    pyautogui.moveTo(chat_xy[0],chat_xy[1])
    pyautogui.click()          # Click the mouse.

    time.sleep(sleep_interval) # delay 1/2 detik (responsiveness)

    # Tekan close country pada number pad (untuk manual ketik +62, berlaku untuk selain +62)
    pyautogui.moveTo(chat_prompt_xy[0],chat_prompt_xy[1])
    pyautogui.click()          # Click the mouse.

    time.sleep(sleep_interval) # delay 1/2 detik (responsiveness)

def chat(nama_peserta):
    """
    mengotomatiskan penulisan dan pengiriman pesan teks di WhatsApp Web, yang mencakup emoji, teks tebal, dan baris baru.

    Args:
        nama_peserta (str): Nama peserta yang akan dimasukkan dalam pesan.
    """
    # clear last message di WA apabila ada
    pyautogui.hotkey('ctrl', 'a') # new line
    pyautogui.press('backspace') # send

    # 🎁
    pyautogui.write(f':gift')
    time.sleep(sleep_interval)
    pyautogui.press('enter')   
    
    pyautogui.write(f'*Personalized Card OlympIAE 2025*',interval=typing_delay)
    
    # 🏆
    pyautogui.write(f':trophy')
    time.sleep(sleep_interval)
    pyautogui.press('enter')  
    time.sleep(sleep_interval)  

    pyautogui.hotkey('shift', 'enter') # new line
    pyautogui.write(f'untuk: *{nama_peserta}*',interval=typing_delay)
    pyautogui.hotkey('shift', 'enter') # new line

    pyautogui.press('enter') # send

    pyautogui.click()          # Click the mouse.

def send_file(bib_number):
    """
    mengotomatiskan proses pengiriman file .zip melalui WhatsApp Web dengan menggunakan pyautogui untuk mengontrol mouse dan keyboard. Fungsi ini mengasumsikan koordinat mouse dan keyboard tertentu sesuai dengan tata letak WhatsApp Web.

    Args:
        bib_number (int): Nomor BIB peserta, yang digunakan untuk mencari file .zip yang sesuai.
    """
    attach_file_xy = [501,688]
    attach_document_xy = [502,556]
    directory_path_xy = [567,54]
    file_path_xy = [729,57]
    file_zip_xy = [323,133]
    send_xy = [972,681]

    # Attach File
    pyautogui.moveTo(attach_file_xy[0],attach_file_xy[1])
    time.sleep(sleep_interval)  
    pyautogui.click()          # Click the mouse.
    time.sleep(3*sleep_interval)  

    # Select document
    pyautogui.press('tab') 
    pyautogui.press('tab') 
    time.sleep(sleep_interval)
    pyautogui.press('down')
    time.sleep(sleep_interval)
    pyautogui.press('down')
    time.sleep(sleep_interval)
    pyautogui.press('enter')
    time.sleep(sleep_interval)

    # Select Directory of File
    pyautogui.moveTo(directory_path_xy[0],directory_path_xy[1])
    time.sleep(sleep_interval)  
    pyautogui.click()          # Click the mouse.
    pyautogui.press('backspace') 
    time.sleep(3*sleep_interval)  
    pyautogui.write('C:\\Users\\ASUS\\Documents\\PersonalizedCardOlympIAE\\PersonalizedCardOlympIAE\\app\\outpu',interval=typing_delay) # tidak sampai selesai
    pyautogui.press('down')
    time.sleep(sleep_interval)
    pyautogui.press('enter')
    time.sleep(sleep_interval)

    # Select/Search File (.zip)
    pyautogui.moveTo(file_path_xy[0],file_path_xy[1])
    time.sleep(sleep_interval)  
    pyautogui.click()          # Click the mouse.
    time.sleep(sleep_interval)  
    pyautogui.write(f'{bib_number:04d}_',interval=typing_delay)
    time.sleep(2*sleep_interval)  

    # Attach File (.zip)
    pyautogui.moveTo(file_zip_xy[0],file_zip_xy[1])
    time.sleep(2*sleep_interval)  
    pyautogui.click()          # Click the mouse.
    time.sleep(2*sleep_interval)   
    pyautogui.press('enter')   

    # Press the Send button
    pyautogui.moveTo(send_xy[0],send_xy[1])
    time.sleep(4*sleep_interval)  
    pyautogui.click()          # Click the mouse.

def send_file_whatsapp(bib_number, debug=False, verbose=True):
    """
    mengirim file melalui WhatsApp ke nomor telepon peserta yang sesuai dengan nomor BIB yang diberikan. Dalam mode debug, fungsi hanya mencetak posisi mouse saat ini. Dalam mode non-debug, fungsi membaca data peserta dari file Excel, mencari nomor telepon berdasarkan nomor BIB, membuka WhatsApp Web, mencari kontak, dan mengirim file.

    Args:
        bib_number (int): Nomor BIB peserta.
        debug (bool, opsional): Jika True, hanya cetak posisi mouse. Jika False, kirim file melalui WhatsApp. Defaultnya False.
    """
    if debug:
        currentMouseX, currentMouseY = pyautogui.position() # Get the XY position of the mouse.
        print(currentMouseX, currentMouseY)
    else: # not debug mode
        try:
            input_file_path = "./input/input_data.xlsx"
            df_podium = pd.read_excel(input_file_path, sheet_name="Podium", engine="openpyxl", converters={'Telp': str})
            peserta = df_podium[df_podium['BIB Peserta'] == bib_number]

            no_telp = peserta['Telp'].iloc[0]
            nama_peserta = peserta['Nama Individu'].iloc[0]
            # Ubah angka pertama '0' menjadi '62'
            if no_telp.startswith("0"):
                no_telp = "62" + no_telp[1:]

            # Ganti tab (VSCode -> WA)
            pyautogui.hotkey('alt', 'tab')
            escape()
            moving(no_telp)
            chat(nama_peserta=nama_peserta)
            send_file(bib_number=bib_number)
            
            # Ganti tab (WA -> VSCode)
            pyautogui.hotkey('alt', 'tab')
            if verbose: print(f"✅ Proses kirim ke Whatsapp untuk peserta: {nama_peserta} (no. BIB: {bib_number:04d}) berhasil.")
            return True
        except:
            if verbose: print(f"❌ Proses kirim ke whatsapp gagal")
            return False
