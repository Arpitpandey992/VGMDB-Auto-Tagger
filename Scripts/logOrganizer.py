import os
import shutil


extensions = ['.log', 'cue', '.m3u', '.txt', '.m3u8', '.mht', '.nfo', '.accurip', '.sfv', '.md5', '.url']


def is_file_a_log(fileName):
    for extension in extensions:
        if fileName.lower().endswith(extension):
            return True
    return False


def move_logs(dir):
    for file in os.listdir(dir):
        # skip the folder if it's already named Logs
        if os.path.basename(dir).lower() == "logs":
            continue
        file_path = os.path.join(dir, file)

        # if the file is a directory, recursively call the function
        if os.path.isdir(file_path):
            move_logs(file_path)

        elif is_file_a_log(file):
            logs_dir = os.path.join(dir, 'Logs')

            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            print(f"Moved : {file} to {logs_dir}")
            shutil.move(file_path, logs_dir)


# prompt the user for the directory to search
directory = "/run/media/arpit/DATA/OSTs/Anime/Re-Zero"

print("Started...")
move_logs(directory)
print("Finished!")
