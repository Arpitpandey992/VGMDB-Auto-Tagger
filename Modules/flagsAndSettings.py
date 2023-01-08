
BACKUPFOLDER = '/run/media/arpit/DATA/backups'
APICALLRETRIES = 5
tableFormat = 'pretty'


class Flags:
    def __init__(self):
        # Management Flags
        self.BACKUP = False
        self.YES = False
        self.CONFIRM = False
        self.RENAME = True
        self.TAG = True
        self.MOVE = False
        self.NO_AUTH = False

        # Metadata Flags
        self.PICS = True
        self.SCANS = True
        self.DATE = True
        self.YEAR = True
        self.CATALOG = True
        self.BARCODE = True

        self.ORGANIZATIONS = True
        # these tags are supposed to be track specific, but in VGMDB, they are provided for entire album,
        # hence i've turned these off.
        self.ARRANGERS = False
        self.COMPOSERS = False
        self.PERFORMERS = False
        self.LYRICISTS = False

        # languages to be probed from VGMDB in the given order of priority
        self.languages = ['ja-latn', 'Romaji', 'en', 'English',
                          'English (Apple Music)', 'ja', 'Japanese']
