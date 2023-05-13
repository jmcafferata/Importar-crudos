import os
import shutil
import subprocess
from pathlib import Path
import win32api
import pywintypes
import scripts.upload_video as upload_video
import scripts.concat as concat


def get_volume_label(drive_letter):
    """Get the volume label for a drive letter"""
    try:
        drive_letter = drive_letter[:-1]
        volume_name_buffer = win32api.GetVolumeInformation(f"{drive_letter}:\\")[0]
        return volume_name_buffer
    except pywintypes.error:
        return ""


def main():
    project_name = input("Enter project name: ")

    drives = [f"{chr(i)}:" for i in range(65, 91) if os.path.exists(f"{chr(i)}:")]
    print("Available Drives:")
    for i, drive in enumerate(drives):
        print(f"{i + 1}. {drive}" + " " + get_volume_label(str(drive)))

    camera_drive_index = int(input("Select Sony A7 drive from list (enter index): ")) - 1
    google_drive_index = int(input("Select jmcafferata@gmail.com virtual drive from list (enter index): ")) - 1
    data_drive_index = int(input("Select Data drive from list (enter index): ")) - 1

    camera_drive = drives[camera_drive_index]
    google_drive = drives[google_drive_index]
    data_drive = drives[data_drive_index]

    camera_drive = os.path.join(camera_drive, "PRIVATE", "M4ROOT", "CLIP")

    folders = [f for f in os.listdir(camera_drive) if os.path.isdir(os.path.join(camera_drive, f))]
    print("you are in: "+ camera_drive)
    print("Available Folders:")
    for i, folder in enumerate(folders):
        print(f"{i + 1}. {folder}")

    folder_index = int(input("Select folder from list (enter index): ")) - 1
    camera_drive = os.path.join(camera_drive, folders[folder_index])
    print("Footage source folder: "+ camera_drive)

    data_rf_path = os.path.join(data_drive, "TOXI", project_name, "RF")
    proxies_path = os.path.join(data_rf_path, "Proxies")
    google_drive_toxi_path = os.path.join(google_drive, "My Drive", "Proyectos", "TOXI", project_name, "RF")

    os.makedirs(data_rf_path, exist_ok=True)
    os.makedirs(proxies_path, exist_ok=True)
    os.makedirs(google_drive_toxi_path, exist_ok=True)
    print("Folders created: ")
    print(data_rf_path)
    print(proxies_path)
    print(google_drive_toxi_path)

    for file in os.listdir(camera_drive):
        if file.endswith(".mp4") or file.endswith(".MP4"):
            print("Copying: " + file)
            shutil.copy(os.path.join(camera_drive, file), data_rf_path)
        else:
            print("Skipping: " + file)

    for file in os.listdir(data_rf_path):
        if file.endswith(".mp4") or file.endswith(".MP4"):
            print("Converting: " + file)
            input_file = os.path.join(data_rf_path, file)
            output_file = os.path.join(proxies_path, f"{file[:-4]}_Proxy.mp4")
            subprocess.run(["ffmpeg", "-i", input_file, "-b:v", "1M", "-vcodec", "h264_nvenc", output_file])
        else:
            print("Skipping: " + file)

    for file in os.listdir(proxies_path):
        if file.endswith("_Proxy.mp4"):
            print("Copying: " + file)
            shutil.copy(os.path.join(proxies_path, file), google_drive_toxi_path)
        else:
            print("Skipping: " + file)

    print("Opening folders in explorer")
    print(data_rf_path)
    print(camera_drive)
    print(google_drive_toxi_path)
    os.startfile(data_rf_path)
    os.startfile(camera_drive)
    os.startfile(google_drive_toxi_path)

    # find Desktop\New project\x.prproj and paste it in the google drive folder parent
    user_desktop = os.path.expanduser("~/Desktop")
    new_project_folder = os.path.join(user_desktop, "New project")
    x_file = os.path.join(new_project_folder, "x.prproj")
    parent_folder = os.path.dirname(google_drive_toxi_path)
    shutil.copy(x_file, parent_folder)
    # rename the x file to the project name
    os.rename(os.path.join(parent_folder, "x.prproj"), os.path.join(parent_folder, project_name + ".prproj"))
    # open the project file
    os.startfile(os.path.join(parent_folder, project_name + ".prproj"))
    
    delete = input("Everything copied correctly? (y/n): ")
    if delete == "y":
        print("Deleting: " + camera_drive)
        shutil.rmtree(camera_drive)
    else:
        print("Not deleting: " + camera_drive)


    # ask the user if they want to upload the footage to youtube
    upload = input("Upload to youtube? (y/n): ")
    if upload == "y":

        # use ffmpeg to turn all the proxies inside the google drive folder into a single video
        concat.merge_videos(google_drive_toxi_path, "concat.mp4")

        # upload the video to youtube
        # Set the values of the variables
        # get concat file in google drive folder
        file = os.path.join(google_drive_toxi_path, "concat.mp4")
        print("Uploading: " + file)
        title = project_name + " - Crudos"

        # Call the upload_video function with the variables
        subprocess.run(["python", "scripts/upload_video.py", "--file", file, "--title", title])

        print("Uploading: " + file)


    else:
        print("Not uploading to youtube")




if __name__ == "__main__":
    main()