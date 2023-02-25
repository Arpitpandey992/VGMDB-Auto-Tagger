import os


def replace_characters(root_dir):
    for subdir, dirs, files in os.walk(root_dir):
        for old_dir in dirs:
            new_dir = old_dir.replace('／', 'Ⳇ')
            if new_dir != old_dir:
                old_dir_path = os.path.join(subdir, old_dir)
                new_dir_path = os.path.join(subdir, new_dir)
                os.rename(old_dir_path, new_dir_path)
                print(f"renamed {old_dir} to {new_dir}")
        for file in files:
            old_file = os.path.join(subdir, file)
            new_file = os.path.join(subdir, file.replace('／', 'Ⳇ'))
            if new_file != old_file:
                os.rename(old_file, new_file)
                print(f"renamed {old_file} to {new_file}")


if __name__ == '__main__':
    root_dir = '/run/media/arpit/DATA/Music/Visual Novels/Steins;Gate'
    replace_characters(root_dir)
