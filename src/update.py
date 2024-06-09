import os
import requests
import json

from typing import Any, Optional, Final

from structs import Mapper


_base_url: Final[str] = 'https://raw.githubusercontent.com/zer0k-z/kz-map-info/master/'

_fext: Final[str] = '.json'
_min_fext: Final[str] = '.min' + _fext

_fnames: Final[dict[str, str]] = {
    'MapsWithMappers': 'maps',
    'MapsWithMappers_Global': 'global',
    'MapsWithMappers_NonGlobal': 'non-global',
    'IncompletedMaps': 'uncompleted'
}

_dest_dir: Final[str] = f'{os.path.dirname(__file__)}/../'

_json_indent: Final[int] = 4
_json_separators: Final[tuple[str, str]] = (',', ':')

_mapper_name_key: Final[str] = 'mapper_name'
_mapper_id64_key: Final[str] = 'mapper_steamid64'
_mappers_key: Final[str] = 'mappers'
_str_separator: Final[str] = ', '

_url_keys: Final[tuple[str, ...]] = ('workshop_url', )

_file_encoding: Final[str] = 'utf-8'
_escape_encoding: Final[str] = 'unicode-escape'


def _unescape(s: Optional[str]) -> Optional[str]:
    if not s:
        return s

    # Fix unicode escaped characters
    return s.encode(_escape_encoding) \
        .replace(b'\\\\u', b'\\u') \
        .decode(_escape_encoding)


def _get_json(file_name: Optional[str]) -> Optional[list[dict[str, Any]]]:
    if not file_name:
        return None

    return requests.get(_base_url + file_name + _fext) \
        .json()


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

    if _mapper_name_key in map_json:
        mapper_names = _str_to_list(map_json[_mapper_name_key], _str_separator)
        del map_json[_mapper_name_key]

    if _mapper_id64_key in map_json:
        mapper_id64s = _str_to_list(map_json[_mapper_id64_key], _str_separator)
        del map_json[_mapper_id64_key]

    length: Final[int] = max(len(mapper_names), len(mapper_id64s))

    _norm_list(mapper_names, length)
    _norm_list(mapper_id64s, length)

    mappers: Final[list[Optional[Mapper]]] = []

    for i in range(length):
        mappers.append(Mapper(mapper_names[i], mapper_id64s[i]))

    map_json[_mappers_key] = mappers


def _fix_urls(map_json: Optional[dict[str, Any]]) -> None:
    if not map_json:
        return

    for key in _url_keys:
        url: str = map_json[key]
        # noinspection HttpUrlsUsage
        map_json[key] = url.replace('http://', 'https://', 1) \
            .replace('/?', '?', 1)


def _fix_maps(maps_json: Optional[list[dict[str, Any]]]) -> None:
    if not maps_json:
        return None

    for map_json in maps_json:
        _fix_mappers(map_json)
        _fix_urls(map_json)


def _dump_maps(file_name: Optional[str], maps_json: Optional[list[dict[str, Any]]]) -> None:
    if not file_name \
            or not maps_json:
        return

    dest: Final[str] = _dest_dir + file_name

    with open(dest + _fext, 'w', encoding=_file_encoding) as file:
        file.write(_unescape(json.dumps(maps_json, indent=_json_indent)))

    with open(dest + _min_fext, 'w', encoding=_file_encoding) as file:
        file.write(_unescape(json.dumps(maps_json, separators=_json_separators)))


if __name__ == '__main__':
    for fkey, fname in _fnames.items():
        maps: list[dict[str, Any]] = _get_json(fkey)

        _fix_maps(maps)
        _dump_maps(fname, maps)
