#!python3.9

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

import os
import requests
import json

from typing import Any, Optional, Final
from requests import Response
from structs import Mapper


_OPEN_FILE_WRITE_FLAG: Final[str] = 'w'
_OPEN_FILE_READ_FLAG: Final[str] = 'r'

_STRING_ENCODE_ERROR_STRICT: Final[str] = 'strict'
_STRING_ENCODE_ERROR_REPLACE: Final[str] = 'replace'
_STRING_ENCODE_ERROR_IGNORE: Final[str] = 'ignore'

_CURRENT_PATH: Final[str] = os.path.dirname(__file__)
_PARENT_PATH: Final[str] = os.path.join(_CURRENT_PATH, '..')

_BASE_URL: Final[str] = 'https://raw.githubusercontent.com/zer0k-z/kz-map-info/master/'

_FILE_NAMES: Final[dict[str, str]] = {
    'MapsWithMappers': 'maps',
    'MapsWithMappers_Global': 'global',
    'MapsWithMappers_NonGlobal': 'non-global',
    'IncompletedMaps': 'uncompleted'
}

_ID_KEY: Final[str] = 'id'
_NAME_KEY: Final[str] = 'name'
_MAPPER_NAME_KEY: Final[str] = 'mapper_name'
_MAPPER_ID64_KEY: Final[str] = 'mapper_steamid64'
_MAPPERS_KEY: Final[str] = 'mappers'
_STR_SEPARATOR: Final[str] = ', '

_URL_KEYS: Final[tuple[str, ...]] = ('workshop_url',)
_INT_KEYS: Final[tuple[str, ...]] = ('id', 'difficulty')

_JSON_INDENT: Final[int] = 4
_JSON_SEPARATORS: Final[tuple[str, str]] = (',', ':')
_JSON_ENSURE_ASCII: Final[bool] = False

_ESCAPE_ENCODING: Final[str] = 'unicode-escape'
_ESCAPE_ENCODING_ERROR: Final[str] = _STRING_ENCODE_ERROR_REPLACE

_DUMP_JSON_FILE_EXT: Final[str] = '.json'
_DUMP_JSON_FILE_MIN_EXT: Final[str] = f'.min{_DUMP_JSON_FILE_EXT}'
_DUMP_JSON_FILE_ENCODING: Final[str] = 'utf-8'


def _unescape(s: Optional[str]) -> Optional[str]:
    if not s:
        return s

    # Fix unicode escaped characters.
    return s.encode(_ESCAPE_ENCODING, errors=_ESCAPE_ENCODING_ERROR) \
        .replace(b'\\\\u', b'\\u') \
        .decode(_ESCAPE_ENCODING, errors=_ESCAPE_ENCODING_ERROR)


def _get_url_response(url: Optional[str]) -> Optional[Response]:
    if not url:
        return None

    response: Final[Response] = requests.get(url)
    response.raise_for_status()

    if response.status_code == 204:
        return None

    return response


def _get_url_json(url: Optional[str]) -> Optional[Any]:
    response: Final[Response] = _get_url_response(url)
    if response is None:
        return None

    return response.json()


def _str_to_list(val: Optional[str], sep: Optional[str] = None) -> Optional[list[str]]:
    if not val:
        return None

    return val.split(sep)


def _norm_list(values: Optional[list[Any]], size: Optional[int]) -> None:
    if values is None \
            or size is None \
            or size < 0:
        return

    length: Final[int] = len(values)

    if length > size:
        del values[size:]
    else:
        values.extend([None] * (size - length))


def _fix_mappers(map_json: Optional[dict[str, Any]]) -> None:
    if not map_json:
        return

    mapper_names: list[str] = []
    mapper_id64s: list[str] = []

    if _MAPPER_NAME_KEY in map_json:
        mapper_names = _str_to_list(map_json[_MAPPER_NAME_KEY], _STR_SEPARATOR)
        del map_json[_MAPPER_NAME_KEY]

    if _MAPPER_ID64_KEY in map_json:
        mapper_id64s = _str_to_list(map_json[_MAPPER_ID64_KEY], _STR_SEPARATOR)
        del map_json[_MAPPER_ID64_KEY]

    length: Final[int] = max(len(mapper_names), len(mapper_id64s))

    _norm_list(mapper_names, length)
    _norm_list(mapper_id64s, length)

    mappers: Final[list[Optional[Mapper]]] = []

    for i in range(length):
        mappers.append(Mapper(mapper_names[i], mapper_id64s[i]))

    map_json[_MAPPERS_KEY] = mappers


def _fix_urls(map_json: Optional[dict[str, Any]]) -> None:
    if not map_json:
        return

    for key in _URL_KEYS:
        url: str = map_json[key]
        # noinspection HttpUrlsUsage
        map_json[key] = url.replace('http://', 'https://', 1) \
            .replace('/?', '?', 1)


def _fix_types(map_json: Optional[dict[str, Any]]) -> None:
    if not map_json:
        return

    for key in _INT_KEYS:
        val: Optional[Any] = map_json.get(key)
        if not val:
            continue

        map_json[key] = int(val)


def _fix_maps(maps_json: Optional[list[dict[str, Any]]]) -> None:
    if not maps_json:
        return None

    for map_json in maps_json:
        _fix_mappers(map_json)
        _fix_urls(map_json)
        _fix_types(map_json)


def _dump_json(
    file_path: Optional[str],
    file_name: Optional[str],
    json_object: Optional[Any]
) -> bool:
    if file_path is None \
            or not json_object:
        return False

    file_path = os.path.normpath(file_path)

    if not file_name:
        if not file_path:
            return False

        file_base_name: Final[str] = os.path.basename(file_path)
        file_split_ext: Final[tuple[str, str]] = os.path.splitext(file_base_name)

        file_path = os.path.dirname(file_path)
        file_name = file_split_ext[0]

    if file_path \
            and not os.path.exists(file_path):
        os.makedirs(file_path)

    dump_path: Final[str] = os.path.join(file_path, file_name)

    with open(dump_path + _DUMP_JSON_FILE_EXT, _OPEN_FILE_WRITE_FLAG, encoding=_DUMP_JSON_FILE_ENCODING) as file:
        file.write(_unescape(json.dumps(json_object, ensure_ascii=_JSON_ENSURE_ASCII, indent=_JSON_INDENT)))

    with open(dump_path + _DUMP_JSON_FILE_MIN_EXT, _OPEN_FILE_WRITE_FLAG, encoding=_DUMP_JSON_FILE_ENCODING) as file:
        file.write(_unescape(json.dumps(json_object, ensure_ascii=_JSON_ENSURE_ASCII, separators=_JSON_SEPARATORS)))

    return True


def _main() -> None:
    for fkey, fname in _FILE_NAMES.items():
        maps_json: Optional[Any] = _get_url_json(_BASE_URL + fkey + _DUMP_JSON_FILE_EXT)
        if not maps_json:
            return

        _fix_maps(maps_json)

        is_success: bool = _dump_json(_PARENT_PATH, fname, maps_json)
        if not is_success:
            return

        dump_path = os.path.join(_PARENT_PATH, fname)
        for map_json in maps_json:
            is_success = _dump_json(dump_path, map_json[_NAME_KEY], map_json)
            if not is_success:
                return

        for map_json in maps_json:
            is_success = _dump_json(dump_path, str(map_json[_ID_KEY]), map_json)
            if not is_success:
                return


if __name__ == '__main__':
    try:
        _main()
    except KeyboardInterrupt:
        pass
