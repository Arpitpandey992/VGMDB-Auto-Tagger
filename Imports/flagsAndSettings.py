class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Flags(metaclass=Singleton):
    # Settings
    BACKUPFOLDER: str = '~/Music/Backups'
    tableFormat: str = 'pretty'

    languages: dict[str, list[str]] = {
        'romaji': ['ja-latn', 'Romaji', 'Romaji Translated'],
        'english': ['en', 'English', 'English (Apple Music)', 'English/German', 'English localized', 'English (alternate)', 'English Translated', 'English [Translation]'],
        'japanese': ['ja', 'Japanese']
    }

    # Management Flags
    BACKUP: bool = False
    YES: bool = False
    CONFIRM: bool = False
    RENAME_FILES: bool = True
    TAG: bool = True
    RENAME_FOLDER: bool = True
    NO_AUTH: bool = False
    NO_INPUT: bool = False
    TRANSLATE: bool = False
    DISC_NUMBERS: bool = True
    TRACK_NUMBERS: bool = True
    IGNORE_MISMATCH: bool = False  # Dangerous, keep false

    # Metadata Flags
    PICS: bool = True
    PIC_OVERWRITE: bool = False
    SCANS: bool = True
    DATE: bool = True
    YEAR: bool = True
    CATALOG: bool = True
    BARCODE: bool = True
    TITLE: bool = True
    KEEP_TITLE: bool = False
    SAME_FOLDER_NAME: bool = False
    ALL_LANG: bool = True

    ORGANIZATIONS: bool = True
    # these tags are supposed to be track specific, but in VGMDB, they are provided for entire album,
    # hence i've turned these off.
    ARRANGERS: bool = False
    COMPOSERS: bool = False
    PERFORMERS: bool = False
    LYRICISTS: bool = False

    # default naming templates
    folderNamingTemplate: str = "{[{date}] }{albumname}{ [{catalog}]}{ [{format}]}"
    # languages to be probed from VGMDB in the given order of priority
    languageOrder: list[str] = ['english', 'romaji', 'japanese']

    # misc flags
    SEE_FLAGS: bool = False


if __name__ == "__main__":
    x = Flags()
    print(x.tableFormat)
    x.tableFormat = "damn_pretty"
    print(x.tableFormat)
    y = Flags()
    print(y.tableFormat)
    assert (x.tableFormat == y.tableFormat)
    assert (x is y)
