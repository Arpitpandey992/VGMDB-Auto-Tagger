import os
import shutil

# Specify the directory to search
directory = "/run/media/arpit/DATA/Downloads/Browser Downloads/yurisa"
DELETE_AS_WELL = True


for item in os.listdir(directory):
    item_path = os.path.join(directory, item)
    if os.path.isdir(item_path) and not os.path.islink(item_path):
        items_in_folder = os.listdir(item_path)
        if len(items_in_folder) == 2 and "cover.jpg" in items_in_folder:
            other_file = [f for f in os.listdir(item_path) if f != "cover.jpg"][0]
            shutil.move(os.path.join(item_path, other_file), os.path.join(directory, other_file))
            print(f"move : {os.path.join(item_path, other_file)} to {os.path.join(directory, other_file)}")
            if DELETE_AS_WELL:
                os.remove(os.path.join(item_path, "cover.jpg"))
                print(f'delete : {os.path.join(item_path, "cover.jpg")}')
                # check if the directory is now empty
                if (len(os.listdir(item_path)) == 0):
                    print(f'delete empty directory: {item_path}')
                    os.rmdir(item_path)
