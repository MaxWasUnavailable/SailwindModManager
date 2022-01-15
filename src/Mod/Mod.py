from dataclasses import dataclass, field


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


if __name__ == '__main__':
    mod = Mod("Testmod", "Testmod", description="This is a test mod object.", author="Max", version="1.0.3", game_version="1.2.13b", tags=["Test", "Multiplayer", "Items"], requirements=["TestModCore"], download_url="localhost")
    print(mod)
