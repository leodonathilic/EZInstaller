import os
import psutil
import csv
from time import sleep
import subprocess
import zipfile
import webbrowser
import requests


def clear():
    os.system('cls')

BANNER = r'''
  ______ ______  _____           _        _ _ 
 |  ____|___  / |_   _|         | |      | | |
 | |__     / /    | |  _ __  ___| |_ __ _| | |
 |  __|   / /     | | | '_ \/ __| __/ _` | | |
 | |____ / /__   _| |_| | | \__ \ || (_| | | |
 |______/_____| |_____|_| |_|___/\__\__,_|_|_|
                                              
by Léo DONATH-ILIC
'''

possible_disks = []
root_path = r"\Program Files (x86)\Steam\steamapps\common"
csv_file_path = r"files\steamcmd_appid.csv"

packages_to_install = ['psutil', 'requests']
for package in packages_to_install:
    subprocess.check_call(['pip', 'install', package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)



def check_install_files():
    # Set the directory path
    directory = "files"
    filename = os.path.join(directory, "BepInEx_x64_latest.zip")
    filename2 = os.path.join(directory, "steamcmd_appid.csv")

    # Check if the directory exists, create it if not
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Check if both files exist
    if os.path.isfile(filename) and os.path.isfile(filename2):
        pass
    else:
        # Download missing files
        latest_release_url = "https://api.github.com/repos/BepInEx/BepInEx/releases/latest"
        response = requests.get(latest_release_url)
        latest_release_data = response.json()

        if not os.path.isfile(filename):
            download_link_x64 = None
            for asset in latest_release_data["assets"]:
                if "x64" in asset["name"]:
                    download_link_x64 = asset["browser_download_url"]
                    break

            if download_link_x64:
                response = requests.get(download_link_x64, stream=True)
                with open(filename, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=128):
                        file.write(chunk)
               

        if not os.path.isfile(filename2):
            # Download filename2
            filename2_download_link = "https://raw.githubusercontent.com/leodonathilic/EZInstaller/main/files/steamcmd_appid.csv"
            response = requests.get(filename2_download_link, stream=True)
            with open(filename2, 'wb') as file:
                for chunk in response.iter_content(chunk_size=128):
                    file.write(chunk)
           

        



def banner(time, clear_before, clear_after):
    if clear_before == True:
        clear()
    else:
        pass
    print(BANNER)
    sleep(time)
    if clear_after == True:
        clear()
    else:
        pass
banner(3, False, True)



def get_all_disks():

    all_disks = []
    partitions = psutil.disk_partitions(all=True)

    for partition in partitions:
        disk_info = {}

        mount_point = partition.mountpoint

        disk_info["mount_point"] = mount_point

        all_disks.append(disk_info)

    return all_disks

def kill_running_game(selected_folder_path, folder_id):
    for root, dirs, files in os.walk(selected_folder_path):
        for file in files:
            if file.endswith(".exe"):
                process_name = os.path.splitext(file)[0]
                try:
                    for process in psutil.process_iter(['pid', 'name']):
                        if process_name.lower() in process.info['name'].lower():
                            print(f"Killing process: {process.info['name']} (PID: {process.info['pid']})")
                            psutil.Process(process.info['pid']).terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass



def check_bepinex_status(selected_folder_path):
    bepinex_directory = os.path.join(selected_folder_path, "BepInEx")
    if os.path.exists(bepinex_directory) and os.path.isdir(bepinex_directory):
        #print("BepInEx directory found:")
        #print(bepinex_directory)
        
        # Check contents of the BepInEx directory
        contents = os.listdir(bepinex_directory)
        
        if len(contents) == 1 and contents[0] == "core":
            #print("[Debug] BepInEx is not installed properly. Only 'core' directory found.")
            return "BepInEx: Not installed properly"
        elif len(contents) > 1:
            #print("[Debug] BepInEx is installed properly. Additional components found.")
            return "BepInEx: Installed!"
    else:
        #print("[Debug] BepInEx directory not found. It's not installed.")
        return "BepInEx: Not installed..."
    #selected_folder_path = ""



def configure_bepinex(subdirectory, folder_id, selected_folder_path):
    print(f"Configuring BepInEx for {subdirectory}...")
    subprocess.run(["cmd", "/c", f"start steam://run/{folder_id}"])
    is_bepinex_deployed = selected_folder_path + r"\BepInEx\Plugins"
    print("Checking deployment...")
    while True:
        try:
            if os.path.exists(is_bepinex_deployed) and os.path.isdir(is_bepinex_deployed):
                kill_running_game(selected_folder_path, folder_id)
                print("Configuration complete. Going back to menu...")
                sleep(2)
                clear()
                find_folder(root_path)
                break
            else:
                
                pass
        except Exception as exception_de_tes_morts:
            print(exception_de_tes_morts)
    
    

def install_bepinex(selected_folder_path):
    bepinex_zip_path = r'files\BepInEx_x64_latest.zip'
    with zipfile.ZipFile(bepinex_zip_path, 'r') as zip_ref:
        zip_ref.extractall(selected_folder_path)

def find_folder(root_path):
    check_install_files()
    banner(0, True, False)
    get_all_disks()
    subdirectories = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
    game_menu = {}
    for i, subdirectory in enumerate(subdirectories, 1):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            match_found = False  # Flag to track if a match is found for the current subdirectory
            for row in reader:
                if len(row) < 2:
                    # Skip rows that do not have enough values
                    continue

                folder_id, folder_name = row
                if folder_name == subdirectory:
                    print(f"{i}.\t{subdirectory} ({folder_id})")
                    game_menu[i] = {"folder_id": folder_id, "subdirectory": subdirectory}
                    match_found = True
                    # You can choose to break here if you want to stop after the first match
            if not match_found:
                pass


    return game_menu

def game_choice_menu():
    game_menu = find_folder(root_path)
    while True:
        print("Please make a choice for the game you want to mod (Enter 0 to exit):")
        try:
            game_choice = int(input())
            if game_choice == 0:
                exit()
            selected_game = game_menu.get(game_choice)
            if selected_game:
                clear()
                banner(0, True, False)
                print("\n\n")
                selected_folder_path = os.path.join(root_path, selected_game['subdirectory'])
                #print(f"Folder directory: {selected_folder_path}")

                bepinex_status = check_bepinex_status(selected_folder_path)
                if bepinex_status == "BepInEx: Installed!":
                    print("\033[92mReady\033[0m")
                    #return selected_folder_path
                    #Want to install mods?
                    install_mods_choice = input("Do you want to install mods? (y/n) ")
                    if install_mods_choice == "y" or install_mods_choice == "Y":
                        #https://thunderstore.io/
                        banner(0, True, False)
                        print("The script will open thunderstore.io (modding community)\n\n")
                        print("Copy the mod file(s) to "+selected_folder_path+r"\BepInEx\plugins")
                        sleep(3)
                        webbrowser.open('https://thunderstore.io')
                        subprocess.Popen(['explorer', selected_folder_path+r"\BepInEx\plugins"], shell=True)
                        input("Thank you for using my script! (Press Enter to exit)")
                        exit()

                    elif install_mods_choice == "n" or install_mods_choice == "N":
                        clear()
                        find_folder(root_path)  


                elif bepinex_status == "BepInEx: Not installed properly":
                    complete_install_choice = input("\033[93mNot installed correctly, do you want to install it?\033[0m (y/n) ")
                    if complete_install_choice == "y" or complete_install_choice == "Y":
                        configure_bepinex(selected_game['subdirectory'], selected_game['folder_id'], selected_folder_path)
                        bepinex_status = "BepInEx: Installed!"
                    elif complete_install_choice == "n" or complete_install_choice == "N":
                        clear()
                        find_folder(root_path)

                    else:
                        pass
                elif bepinex_status == "BepInEx: Not installed...":
                    install_choice = input("\033[93mNot installed, do you want to install it?\033[0m (y/n) ")
                    if install_choice == "y" or install_choice == "Y":
                        install_bepinex(selected_folder_path)
                        configure_bepinex(selected_game['subdirectory'], selected_game['folder_id'], selected_folder_path)
                        bepinex_status = "BepInEx: Installed!"
                    elif install_choice == "n" or install_choice == "N":
                        clear()
                        find_folder(root_path)    

                    

                    

            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

game_choice_menu()
