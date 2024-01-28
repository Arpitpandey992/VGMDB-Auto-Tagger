from Modules.Mutagen.mutagen_wrapper import AudioFactory
import os

directory = "/run/media/arpit/DATA/Downloads/Torrents/New Folder/The Door into Next Season EP (Little Busters! arrange) [N-A]"

folder_name = os.path.basename(directory)

start_index = folder_name.index('[')
end_index = folder_name.index(']')

# Extract the name and catalog using slicing
name = folder_name[:start_index].strip()
catalog = folder_name[start_index + 1:end_index].strip()
print(name, catalog)
items = os.listdir(directory)

# Count the number of items
num_items = len(items)

for item in os.listdir(directory):
    item_path = os.path.join(directory, item)
    audio = AudioFactory.buildAudioManager(item_path)
    audio.setAlbum([name])
    audio.setCatalog(catalog)
    trackNumber = audio.getTrackNumber()
    if trackNumber:
        audio.setTrackNumbers(trackNumber, str(num_items))
    audio.setDiscNumbers('1', '1')
    oldName = audio.getTitle()
    if oldName:
        newName = oldName.replace(f" - {name}", "", 1)
        audio.setTitle([newName])
    date = audio.getDate()
    if date and "-" not in date:
        newDate = date[:4] + "-" + date[4:6] + "-" + date[6:]
        audio.setDate(newDate)
    print(f"done for: {item}")
    audio.save()
