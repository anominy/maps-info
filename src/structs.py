#  Maps Info
#
#  Copyright (C) 2024  anominy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Optional, Final, Any, Callable


class Mapper(dict):
    NAME_KEY: Final[str] = 'name'
    ID64_KEY: Final[str] = 'id64'

    def __init__(self, name: Optional[Any], id64: Optional[Any]) -> None:
        super().__init__()

        self[Mapper.NAME_KEY] = self.__fix_val(name, str)
        self[Mapper.ID64_KEY] = self.__fix_val(id64, int)

    @property
    def name(self) -> Optional[str]:
        return self[Mapper.NAME_KEY]

    @property
    def id64(self) -> Optional[int]:
        return self[Mapper.ID64_KEY]

    @staticmethod
    def __fix_val(s: Optional[Any], type: Callable[[Any], Any]) -> Optional[Any]:
        return type(s) if s and s != 'null' else None
