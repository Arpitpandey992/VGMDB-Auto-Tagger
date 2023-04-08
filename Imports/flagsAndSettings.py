BACKUPFOLDER = '~/Music/Backups'
APICALLRETRIES = 5
tableFormat = 'pretty'

languages = {
    'romaji': ['ja-latn', 'Romaji', 'Romaji Translated'],
    'english': ['en', 'English', 'English (Apple Music)', 'English/German', 'English localized', 'English (alternate)', 'English Translated', 'English [Translation]'],
    'japanese': ['ja', 'Japanese']
}


class Flags:
    def __init__(self):
        # Management Flags
        self.BACKUP = False
        self.YES = False
        self.CONFIRM = False
        self.RENAME_FILES = True
        self.TAG = True
        self.RENAME_FOLDER = True
        self.NO_AUTH = False
        self.NO_INPUT = False
        self.TRANSLATE = False
        self.DISC_NUMBERS = True
        self.TRACK_NUMBERS = True
        self.IGNORE_MISMATCH = False  # Dangerous, keep false

        # Metadata Flags
        self.PICS = True
        self.PIC_OVERWRITE = False
        self.SCANS = True
        self.DATE = True
        self.YEAR = True
        self.CATALOG = True
        self.BARCODE = True
        self.TITLE = True
        self.KEEP_TITLE = False
        self.ALL_LANG = True

        self.ORGANIZATIONS = True
        # these tags are supposed to be track specific, but in VGMDB, they are provided for entire album,
        # hence i've turned these off.
        self.ARRANGERS = False
        self.COMPOSERS = False
        self.PERFORMERS = False
        self.LYRICISTS = False

        # languages to be probed from VGMDB in the given order of priority
        self.languageOrder = ['english', 'romaji', 'japanese']

        # misc flags
        self.SEE_FLAGS = False
