import os
import shutil


def move_logs(dir):
    # loop through all files and directories in the specified directory
    for file in os.listdir(dir):
        # skip the folder if it's already named Logs
        if os.path.basename(dir).lower() == "logs":
            continue
        # construct the full path of the file
        file_path = os.path.join(dir, file)

        # if the file is a directory, recursively call the function
        if os.path.isdir(file_path):
            move_logs(file_path)

        elif file.lower().endswith('.log') or file.lower().endswith('.cue') or file.lower().endswith('.m3u'):
            logs_dir = os.path.join(dir, 'Logs')

            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            print(f"Moved : {file} to {logs_dir}")
            shutil.move(file_path, logs_dir)


# prompt the user for the directory to search
directory = "/run/media/arpit/DATA/Downloads/Torrents/Key Sounds Label/[KSLA-B]"

print("Started...")
move_logs(directory)
print("Finished!")
