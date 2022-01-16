from src.Logger.Loggable import Loggable
from src.Config.Config import Config
from src.Mod.Mod import Mod
from github import Github
from copy import copy
import requests
import json


class ModManager(Loggable):
    """
    Instance of a Mod Manager.
    Handles:
        - Fetching of mod information
        - Caching of mod information (optional)
        - Downloading of mods
        - Managing of mod installation (optional)
    """
    def __init__(self, logger, config: Config = None):
        super(ModManager, self).__init__(logger=logger)
        self.mods: dict[str, Mod] = dict()
        self.config: Config = config or Config()
        self.git: Github = self.__init_git()

        self.filter_tags = []
        self.filter_search = ""

    def __init_git(self, use_token: bool = True) -> Github:
        """
        Initialise the Github connection.
        Uses a token if one is configured in the config.
        :return: Github connection instance
        """
        git_token = None
        if use_token:
            git_token = self.config.config.get("github_access_token", None)
        if git_token:
            return Github(login_or_token=git_token)
        else:
            return Github()

    def parse_mod(self, mod_data: dict, download_url: str = None, image: bytes = None) -> Mod:
        self.log(f"Parsing new mod from {download_url}", is_verbose=True)
        self.log(f"info.json: {str(mod_data)}", is_verbose=True)

        mod_id = mod_data.get("Id")
        name = mod_data.get("DisplayName")
        author = mod_data.get("Author", "")
        mod_version = mod_data.get("Version", "")
        game_version = mod_data.get("GameVersion", "")
        manager_version = mod_data.get("ManagerVersion", "")
        requirements = mod_data.get("Requirements", [])
        home_page = mod_data.get("HomePage", None)
        repository = mod_data.get("Repository", None)
        tags = mod_data.get("Tags", [])
        incompatible = mod_data.get("Incompatible", [])
        modloader_required = mod_data.get("ModloaderRequired", False)
        description = mod_data.get("Description", "")
        additional_fields = mod_data.get("AdditionalFields", None)

        return Mod(
            id=mod_id,
            display_name=name,
            description=description,
            author=author,
            version=mod_version,
            manager_version=manager_version,
            game_version=game_version,
            requirements=requirements,
            incompatible=incompatible,
            tags=tags,
            download_url=download_url,
            home_page=home_page,
            repository=repository,
            image=image,
            modloader_required=modloader_required,
            additional_fields=additional_fields
        )

    def update_mod_list(self, mods: list[Mod]) -> None:
        """
        Updates internal mod dictionary with new mod list.
        :param mods: list of mods to load from.
        """
        for mod in mods:
            self.mods[mod.id] = mod

    def fetch_info(self, second_attempt: bool = False) -> bool:
        """
        Fetches information on all mods from the configured github repositories.
        :return: Whether or not the info refresh was rate limited by Github.
        """
        mods = []
        rate_limited = False
        for repo_id in self.config.config.get("repository_ids", []):
            try:
                repo = self.git.get_repo(repo_id)
                for mod_folder in repo.get_contents("mods"):
                    try:
                        mod_url = mod_folder.url
                        mod_image = None
                        data = None
                        self.log(f"Fetching mod from: \"{mod_url}\"")
                        for file in repo.get_contents(f"mods/{mod_folder.name}"):
                            if file.name == "info.json":
                                data = json.loads(file.decoded_content.decode("utf-8"))
                            if file.name == "mod.png":
                                mod_image = requests.get(file.download_url).content

                        if data is not None:
                            mods.append(self.parse_mod(data, download_url=mod_url, image=mod_image))
                            self.log(f"Parsed new mod: \"{mods[-1].display_name}\"")
                        else:
                            self.log(f"Mod found without info.json file. Please report this to the modding community! Mod in question is: \"{mod_folder.name}\"")
                    except Exception as e:
                        self.log(str(e), is_error=True)
            except Exception as e:
                self.log(str(e), is_error=True)
                if "403" in str(e):
                    rate_limited = True
                if "401" in str(e):
                    self.git = self.__init_git(False)
                    if not second_attempt:
                        self.log("Attempting to refetch without token.")
                        self.fetch_info(True)

        self.update_mod_list(mods)

        return not rate_limited

    def download_mod(self, mod_id) -> None:
        self.log(f"Attempting to download mod: \"{mod_id}\"")
        mod = self.mods.get(mod_id, None)

        if mod is None:
            self.log("Mod not found. Aborting download.")
            return

        downloads_dir = self.config.config.get("downloads_directory", "")
        if mod.download(downloads_dir):
            self.log("Mod downloaded successfully.")
        else:
            self.log("Mod download failed.")

    def clear_mods(self) -> None:
        """
        Clear mod dictionary.
        """
        self.mods.clear()

    def refresh(self, clear: bool = True) -> None:
        """
        Fetch mod information and optionally clear mod dict first.
        :param clear: Whether or not to clear the mod dictionary first.
        """
        if clear:
            self.clear_mods()
        self.fetch_info()

    def add_filter_tag(self, tag: str) -> None:
        self.filter_tags.append(tag)

    def clear_filter_tags(self) -> None:
        self.filter_tags.clear()

    def remove_filter_tag(self, tag: str) -> None:
        self.filter_tags.remove(tag)

    def set_filter_search(self, search: str) -> None:
        self.filter_search = search

    def clear_filter_search(self) -> None:
        self.filter_search = ""

    def apply_filter_tags(self, mods: list[Mod]) -> list[Mod]:
        if len(self.filter_tags) == 0:
            return mods
        filtered_mods = []

        for mod in mods:
            for tag in self.filter_tags:
                if tag in mod.tags:
                    filtered_mods.append(copy(mod))

        return filtered_mods

    def apply_filter_search(self, mods: list[Mod], fuzzy: bool = False) -> list[Mod]:
        """
        TODO: Fuzzy search
        :param mods:
        :param fuzzy:
        :return:
        """
        if self.filter_search == "":
            return mods
        filtered_mods = []

        for mod in mods:
            if self.filter_search in mod.display_name:
                filtered_mods.append(copy(mod))

        return filtered_mods

    def sort_mods(self, mods: list[Mod]) -> list[Mod]:
        return sorted(mods, key=lambda mod: mod.display_name)

    def get_mods(self) -> list[Mod]:
        mods = list(self.mods.values())

        mods_filtered_tags = self.apply_filter_tags(mods)
        mods_filtered_search = self.apply_filter_search(mods_filtered_tags)

        return self.sort_mods(mods_filtered_search)

    def get_installed_mods(self) -> list[Mod]:
        return self.get_mods()

    def install_mod(self, mod_id: str) -> None:
        pass

    def uninstall_mod(self, mod_id: str) -> None:
        pass

    def update_mod(self, mod_id: str) -> None:
        pass
