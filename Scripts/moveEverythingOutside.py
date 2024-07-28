import os
import shutil
import argparse

folderPath = ""
parser = argparse.ArgumentParser(description="Custom task")

parser.add_argument("folderPath", nargs="?", help="Album directory path")
args = parser.parse_args()
if args.folderPath:
    folderPath = args.folderPath
while folderPath[-1] == "/":
    folderPath = folderPath[:-1]

for file in os.listdir(folderPath):
    file_path = os.path.join(folderPath, file)
    if not os.path.isdir(file_path) or not file.startswith("["):
        continue
    for innerFile in os.listdir(file_path):
        innerFilePath = os.path.join(file_path, innerFile)
        shutil.move(innerFilePath, os.path.join(folderPath, innerFile))
        print(f"Moved {innerFilePath} to {folderPath}")
