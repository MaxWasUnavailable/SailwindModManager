from src.Logger.Loggable import Loggable
from src.Config.Config import Config
from src.Mod.Mod import Mod
from shutil import rmtree, copytree
from github import Github
from copy import copy
import requests
import json
import os


class ModManager(Loggable):
    """
    Instance of a Mod Manager.
    Handles:
        - Fetching of mod information
        - Caching of mod information (optional / TODO)
        - Downloading of mods
        - Managing of mod installation (optional / TODO)
    """
    def __init__(self, logger, config: Config = None):
        super(ModManager, self).__init__(logger=logger)
        self.mods: dict[str, Mod] = dict()
        self.installed_mods: dict[str, Mod] = dict()
        self.config: Config = config or Config()
        self.git: Github = self.__init_git()

        self.filter_tags = []
        self.filter_search = ""

        # TODO: Might freeze the GUI for a couple of seconds if you have a lot of mods installed?
        # Issue is, where to refresh these while keeping the fetching & refreshing split up between downloaded & installed mods on the GUI threads?
        self.__refresh_downloaded_mods()
        self.__refresh_installed_mods()

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

    def parse_mod(self, mod_data: dict, download_url: str = None, image: bytes = None, download_dir: str = None, install_dir: str = None) -> Mod:
        """
        Parse a mod's data and return a Mod object.
        :param mod_data: Mod's data as dictionary
        :param download_url: URL where the mod can be downloaded from
        :param image: Bytes object representing the mod's image
        :param download_dir: Provided if the mod has already been downloaded
        :param install_dir: Provided if the mod has already been installed
        :return: Parsed Mod object
        """
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

        mod = Mod(
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
            additional_fields=additional_fields,
            downloaded_dir_path=download_dir,
            installed_dir_path=install_dir
        )

        mod.verify_game_version(self.config.config["game_version"])

        return mod

    def update_mod_list(self, mods: list[Mod], installed: bool = False) -> None:
        """
        # TODO: Might need a force_update parameter where downloaded/installed mod refreshes can be forced to replace existing entries? Might not be necessary though.
        Updates internal mod dictionary with new mod list.
        :param mods: list of mods to load from.
        :param installed: Whether or not to update the installed mod list or downloaded mod list.
        """
        for mod in mods:
            overwrite = False
            if installed:
                existing_entry = self.installed_mods.get(mod.id, None)
            else:
                existing_entry = self.mods.get(mod.id, None)
            if existing_entry is None:
                overwrite = True
            else:
                if existing_entry.downloaded_dir_path is not None:
                    # Existing mod entry is downloaded
                    if mod.downloaded_dir_path is None:
                        # New mod is not downloaded
                        # --> Update download URL in case of local copy not having one, or download URL having updated
                        if installed:
                            self.installed_mods[mod.id].download_url = mod.download_url
                        else:
                            self.mods[mod.id].download_url = mod.download_url

                        if not existing_entry.compare_version(mod):
                            # New mod object is newer in version
                            if installed:
                                self.installed_mods[mod.id].update_available = True
                            else:
                                self.mods[mod.id].update_available = True
                    else:
                        # If *new* entry is downloaded, we (probably always?) have just updated a mod. Hence, overwrite.
                        overwrite = True
                else:
                    # If both aren't downloaded, we received new information. Hence, overwrite.
                    overwrite = True
            if overwrite:
                if installed:
                    self.installed_mods[mod.id] = mod
                    if self.installed_mods[mod.id].download_url is None and existing_entry is not None:
                        # If old entry had a download URL and new one doesn't, update new entry with old download URL.
                        self.installed_mods[mod.id].download_url = existing_entry.download_url
                else:
                    self.mods[mod.id] = mod
                    if self.mods[mod.id].download_url is None and existing_entry is not None:
                        # If old entry had a download URL and new one doesn't, update new entry with old download URL.
                        self.mods[mod.id].download_url = existing_entry.download_url

            # Special check to see if installed mod has an update available:
            if installed:
                downloaded_mod = self.mods.get(mod.id, None)
                if downloaded_mod is not None:
                    if downloaded_mod.downloaded_dir_path is not None:
                        if not self.installed_mods[mod.id].compare_version(downloaded_mod):
                            self.log(f"Update available for installed mod: {mod.id}")
                            self.installed_mods[mod.id].update_available = True

    def fetch_info(self, second_attempt: bool = False) -> bool:
        """
        Fetches information on all mods from the configured github repositories.
        :param second_attempt: Whether or not this is the second attempt already, when retrying after an invalid token was provided. Prevents infinite recursion.
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
                            if file.name in ["mod.png", "mod.jpg"]:
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

    def download_mod(self, mod_id) -> bool:
        """
        Downloads a mod via its given mod_id.
        :param mod_id: Mod id of the mod to download
        :return: Whether or not the download was successful
        """
        self.log(f"Attempting to download mod: \"{mod_id}\"")
        mod = self.mods.get(mod_id, None)

        if mod in [None, ""]:
            self.log("Mod not found. Aborting download.")
            return False

        downloads_dir = self.config.config.get("downloads_directory", "")

        try:
            download_result = mod.download(downloads_dir)
        except Exception as e:
            self.log(f"Mod download failed. Exception: {e}", is_error=True)
            return False

        if download_result:
            self.log("Mod downloaded successfully.")
            self.__refresh_downloaded_mods()
            return True
        else:
            self.log("Mod download failed.")
            return False

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
        self.__refresh_downloaded_mods()
        self.__refresh_installed_mods()
        self.fetch_info()

    def add_filter_tag(self, tag: str) -> None:
        """
        Add tag to tag filter list.
        :param tag: Tag to add to tag filter
        """
        self.filter_tags.append(tag)

    def clear_filter_tags(self) -> None:
        """
        Clear tag filter list.
        """
        self.filter_tags.clear()

    def remove_filter_tag(self, tag: str) -> None:
        """
        Remove tag from tag filter list.
        :param tag: Tag to remove from tag filter
        """
        self.filter_tags.remove(tag)

    def set_filter_search(self, search: str) -> None:
        """
        Set search filter's search term.
        :param search: Search term to use.
        """
        self.filter_search = search

    def clear_filter_search(self) -> None:
        """
        Clear search filter's search term.
        """
        self.filter_search = ""

    def apply_filter_tags(self, mods: list[Mod]) -> list[Mod]:
        """
        Apply tag filter list to provided list of mods.
        :param mods: List of mods to apply the filter to.
        :return: Filtered list of mods.
        """
        if len(self.filter_tags) == 0:
            return mods
        filtered_mods = []

        for mod in mods:
            for tag in self.filter_tags:
                if tag in mod.tags:
                    # Copy to prevent weird behaviour.
                    filtered_mods.append(copy(mod))

        return filtered_mods

    def apply_filter_search(self, mods: list[Mod], fuzzy: bool = False) -> list[Mod]:
        """
        Apply search filter to provided list of mods.
        TODO: Fuzzy search?
        :param mods: List of mods to apply the filter to.
        :param fuzzy: Whether or not to use fuzzy matching. (CURRENTLY UNUSED)
        :return: Filtered list of mods.
        """
        if self.filter_search == "":
            return mods
        filtered_mods = []

        for mod in mods:
            if self.filter_search in mod.display_name:
                filtered_mods.append(copy(mod))

        return filtered_mods

    def sort_mods(self, mods: list[Mod]) -> list[Mod]:
        """
        Sort mods alphabetically.
        :param mods: List of mods to sort.
        :return: Sorted list of mods.
        """
        return sorted(mods, key=lambda mod: mod.display_name)

    def refresh_local_mods(self, directory: str, downloaded: bool = False, installed: bool = False) -> list[Mod]:
        mods = []
        if directory is None:
            self.log("Tried to refresh from local mods directory without a directory being given.", is_error=True)
            return mods

        if not os.path.exists(directory):
            self.log("Tried to refresh from local mods directory with invalid directory specified. This could be because you haven't downloaded any mods yet, or because you don't have a mods folder in the Sailwind directory.", is_error=True)
            return mods

        for local_mod_dir in [os.path.join(directory, mod_dir_name) for mod_dir_name in filter(lambda x: os.path.isdir(os.path.join(directory, x)), os.listdir(directory))]:
            try:
                mod_image = None
                data = None
                self.log(f"Fetching local mod from: \"{local_mod_dir}\"")
                for file in os.listdir(local_mod_dir):
                    if file == "info.json":
                        info_file = open(os.path.join(local_mod_dir, file), 'r')
                        data = json.loads(info_file.read())
                        info_file.close()
                    if file in ["mod.png", "mod.jpg"]:
                        image_file = open(os.path.join(local_mod_dir, file), 'rb')
                        mod_image = image_file.read()
                        image_file.close()

                if data is not None:
                    download_dir = None
                    install_dir = None
                    if downloaded:
                        download_dir = local_mod_dir
                    if installed:
                        install_dir = local_mod_dir
                    mods.append(self.parse_mod(data, image=mod_image, download_dir=download_dir, install_dir=install_dir))
                    self.log(f"Parsed new mod: \"{mods[-1].display_name}\"")
                else:
                    self.log(f"Mod found without info.json file. Please report this to the modding community! Mod in question is: \"{local_mod_dir}\"")
            except Exception as e:
                self.log(str(e), is_error=True)

        self.update_mod_list(mods, installed=installed)

    def __refresh_downloaded_mods(self):
        downloaded_dir = self.config.config.get("downloads_directory", None)
        self.refresh_local_mods(downloaded_dir, downloaded=True)

    def __refresh_installed_mods(self):
        installed_dir = self.config.config.get("mods_directory", None)
        self.installed_mods.clear()
        self.refresh_local_mods(installed_dir, installed=True)

    def get_mod(self, mod_id: str) -> Mod:
        """
        Get a specific mod object if it exists.
        :param mod_id: Mod id of the mod to get
        :return:
        """
        return self.mods.get(mod_id, None)

    def get_mods(self) -> list[Mod]:
        """
        Get list of fetched & filtered mods. Does not re-fetch from repos.
        :return: List of fetched & filtered mods.
        """
        mods = list(self.mods.values())

        mods_filtered_tags = self.apply_filter_tags(mods)
        mods_filtered_search = self.apply_filter_search(mods_filtered_tags)

        return self.sort_mods(mods_filtered_search)

    def get_installed_mods(self, refresh: bool = True) -> list[Mod]:
        """
        Get list of installed mods.
        :param refresh: Whether or not to check the mods directory again for changes.
        :return: List of installed mods.
        """
        if refresh:
            self.__refresh_installed_mods()

        mods = list(self.installed_mods.values())

        installed_mods = []
        for mod in mods:
            if mod.installed_dir_path is not None:
                installed_mods.append(mod)

        return installed_mods

    def install_mod(self, mod_id: str) -> bool:
        """
        Copy a mod from the downloads dir to the installation dir.
        :param mod_id: Mod id of the mod to install
        :return: Whether or not the installation was successful.
        """
        installed_dir = self.config.config.get("mods_directory", None)

        if installed_dir in [None, ""]:
            self.log("Mods directory was not specified. Please check your configuration file.")
            return False

        mod_to_install = self.mods.get(mod_id, None)
        if mod_to_install in [None, ""]:
            self.log("Could not find mod to install since it wasn't found in the mod list.")
            return False

        mod_downloaded_dir = mod_to_install.downloaded_dir_path
        if mod_downloaded_dir in [None, ""]:
            self.log("Could not install mod since it wasn't downloaded.")
            return False

        if not os.path.exists(mod_downloaded_dir):
            self.log("Could not install mod since it wasn't downloaded. Please report this.")
            return False

        if mod_to_install.installed_dir_path not in [None, ""]:
            if os.path.exists(mod_to_install.installed_dir_path):
                self.log("Mod is already installed. Please ensure that there are no leftover files of this mod in the mods directory. Please report this.")
                return False

        folder_name = mod_downloaded_dir.split("/")[-1]

        if os.path.exists(f"{installed_dir}/{folder_name}"):
            self.log("Mod is already installed. Please ensure that there are no leftover files of this mod in the mods directory.")
            return False

        copytree(mod_downloaded_dir, f"{installed_dir}/{folder_name}")

        self.log(f"Mod installed in directory: {installed_dir}/{folder_name}")

        self.__refresh_installed_mods()

        return True

    def uninstall_mod(self, mod_id: str) -> bool:
        """
        Remove a mod from the installation dir.
        :param mod_id: Mod id of the mod to uninstall
        :return: Whether or not the uninstallation was successful.
        """
        installed_mod = self.installed_mods.get(mod_id, None)
        if installed_mod is None:
            self.log("Could not uninstall mod since it wasn't found in the installed mod list.")
            return False
        if os.path.exists(installed_mod.installed_dir_path):
            self.log(f"Uninstalling mod from {installed_mod.installed_dir_path}")
            rmtree(installed_mod.installed_dir_path)
            self.__refresh_installed_mods()
            return True
        else:
            self.log("Could not uninstall mod since the installed path wasn't found. Please report this.")
            return False

    def update_mod(self, mod_id: str, update_install: bool = True, download_first: bool = False) -> bool:
        """
        Update a mod.
        :param mod_id: Mod id of the mod to uninstall
        :param update_install: Whether or not to update the installed mod as well
        :param download_first: Whether or not to force a new download first before updating the installed mod. Generally only useful if you're updating both the download *and* the installed mod at the same time.
        :return: Whether or not the update was successful.
        """
        if update_install:
            success = True
            if download_first:
                success = self.download_mod(mod_id)
            success = success and self.install_mod(mod_id)
            self.__refresh_installed_mods()

        else:
            success = self.download_mod(mod_id)

        return success
