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
        self.load_config(self.config_path)

    def load_config(self, config_path):
        config_file = open(config_path, 'r')
        self.config = yaml.load(config_file)
        config_file.close()
