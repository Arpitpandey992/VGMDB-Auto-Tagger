from mutagen.flac import FLAC

filePath = "/run/media/arpit/DATA/OSTs/Anime/Ginga Eiyuu Densetsu/[2007.10.10] Legend of the Galactic Heroes CD-BOX Galactic Empire SIDE [KICA-859~70]/Disc 02/02 - Symphony No.7 In E Minor ˮlied Der Nachtˮ 4.Nachtmusik Ii(Andante Amoroso).flac"


audio = FLAC(filePath)
print(audio.pprint())
