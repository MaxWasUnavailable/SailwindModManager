from dataclasses import dataclass, field
from ruamel.yaml import YAML

yaml = YAML(typ='safe')


@dataclass
class Config:
    """
    Represents a config.
    """
    config: dict = None
    config_path: str = "./data/config.yaml"

    def __post_init__(self):
        """
        Post init function provided by dataclass.
        Called after initialisation.
        """
        self.load_config(self.config_path)

    def load_config(self, config_path: str = None) -> bool:
        """
        Loads a config from a file path.
        :param config_path: Path to load config file from.
        """
        if config_path is None:
            if self.config_path is None:
                return False
            config_path = self.config_path

        try:
            config_file = open(config_path, 'r')
            self.config = yaml.load(config_file)
            config_file.close()
            return True
        except Exception as e:
            return False

    def save_config(self, config_path: str = None) -> bool:
        """
        Save a config to file.
        :param config_path:  Path to save config to.
        :return: Whether or not the save was successful.
        """
        if config_path is None:
            if self.config_path is None:
                return False
            config_path = self.config_path
        try:
            config_file = open(config_path, 'w')
            yaml.dump(self.config, config_file)
            config_file.close()
            return True
        except Exception as e:
            return False
