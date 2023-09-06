from typing import Optional, Final


class Mapper(dict):
    NAME_KEY: Final[str] = 'name'
    ID64_KEY: Final[str] = "id64"

    def __init__(self, name: Optional[str], id64: Optional[str]) -> None:
        super().__init__()

        self[Mapper.NAME_KEY] = self.__fix_val(name)
        self[Mapper.ID64_KEY] = self.__fix_val(id64)

    @property
    def name(self) -> Optional[str]:
        return self[Mapper.NAME_KEY]

    @property
    def id64(self) -> Optional[str]:
        return self[Mapper.ID64_KEY]

    @staticmethod
    def __fix_val(s: Optional[str]) -> Optional[str]:
        return s if s and s != 'null' else None
