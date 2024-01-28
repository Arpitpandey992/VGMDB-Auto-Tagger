from Modules.VGMDB.user_interface.cli import CLI
from Modules.VGMDB.user_interface.cli_args import get_config_from_args


app = CLI(get_config_from_args())

app.run()
