from dataclasses import dataclass, field
from ast import literal_eval
from os.path import exists
from shutil import rmtree
from os import mkdir
import requests


@dataclass
class Mod:
    """
    Represents a mod.
    """
    id: str
    display_name: str
    description: str = None
    author: str = None
    version: str = None
    manager_version: str = None
    game_version: str = None
    requirements: list = field(default_factory=list)
    incompatible: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    download_url: str = None
    home_page: str = None
    repository: str = None
    image: bytes = None
    modloader_required: bool = False
    additional_fields: dict = field(default_factory=dict)

    def download(self, path="./data/downloads/") -> bool:
        """
        Downloads mod to provided path directory.
        :param path: Directory to download to.
        :return: Whether or not the download was successful.
        """
        parsed_url = literal_eval(requests.get(self.download_url).content.decode("utf-8"))
        if len(parsed_url) == 0:
            return False

        if not exists(path):
            mkdir(path)

        remote_folder_name = parsed_url[0]['path'].split("/")[1]

        full_path = path + remote_folder_name + "/"

        # Delete mod directory if it already exists, to prevent keeping outdated / removed files.
        if exists(full_path):
            rmtree(full_path)
        mkdir(full_path)

        for file in parsed_url:
            file_to_save = open(full_path + file['name'], 'wb')
            file_to_save.write(requests.get(file['download_url']).content)
            file_to_save.close()

        return True


if __name__ == '__main__':
    mod = Mod("Testmod", "Testmod", description="This is a test mod object.", author="Max", version="1.0.3", game_version="1.2.13b", tags=["Test", "Multiplayer", "Items"], requirements=["TestModCore"], download_url="localhost")
    print(mod)
