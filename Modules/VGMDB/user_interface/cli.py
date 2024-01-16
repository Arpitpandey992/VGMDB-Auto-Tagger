import json
import os
from Modules.VGMDB.user_interface.cli_args import CLIArgs


class CLI:
    def __init__(self):
        pass

    def run(self):
        config = self._get_args().get_config()
        print(config)

    # Private Functions
    def _get_args(self) -> CLIArgs:
        cli_args = CLIArgs().parse_args().as_dict()
        file_args = self._get_json_args()
        unexpected_args = set(file_args.keys()) - set(cli_args.keys())
        if unexpected_args:
            raise TypeError(f"unexpected argument in config.json: {', '.join(unexpected_args)}")
        cli_args.update(file_args)  # config file has higher priority
        return CLIArgs().from_dict(cli_args)

    def _get_json_args(self):
        """use config.json in root directory to override args"""
        config_file_path = "config.json"
        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as file:
                file_config = json.load(file)
                return file_config
        return {}
    

if __name__ == "__main__":
    cli_manager = CLI()
    cli_manager.run()
