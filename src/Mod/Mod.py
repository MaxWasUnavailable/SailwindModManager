from dataclasses import dataclass, field


@dataclass
class Mod:
    """
    Represents a mod.
    """
    name: str
    description: str = None
    author: str = None
    version: str = None
    game_version: str = None
    tags: list = field(default_factory=list)
    dependencies: list = field(default_factory=list)
    url: str = None
    image: bytes = None
    additional_fields: dict = field(default_factory=dict)


if __name__ == '__main__':
    mod = Mod("Testmod", description="This is a test mod object.", author="Max", version="1.0.3", game_version="1.2.13b", tags=["Test", "Multiplayer", "Items"], dependencies=["TestModCore"], url="localhost")
    print(mod)
