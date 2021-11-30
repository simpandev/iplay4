#!/usr/bin/env python3
from dataclasses import dataclass, asdict
import json
import logging
from typing import List
import os

import coloredlogs

__author__ = "Simone Pandolfi <simopandolfi@gmail.com>"
__version__ = (1, 0, 0, "salamandra")

log_level = logging.INFO
log_format = "%(asctime)s [%(process)d] %(levelname)s %(message)s"
coloredlogs.install(level=log_level, fmt=log_format)
log = logging.getLogger()


@dataclass
class PlaylistEntry:
    name: str
    id: str


@dataclass
class PlaylistIndex:
    favorite: str
    playlists: List[PlaylistEntry]


@dataclass
class VideoEntry:
    title: str
    author: str
    duration: str
    video_id: str


def get_playlist_id(playlist_name: str) -> str:
    name = playlist_name[1:] if playlist_name.startswith("_") else playlist_name
    return name.lower().replace(" ", "-")


def get_playlist_name(playlist_name: str) -> str:
    return playlist_name[1:] if playlist_name.startswith("_") else playlist_name


def build_playlist_index(input_dir: str) -> PlaylistIndex:

    def search_favorite_playlist(playlists_names: List[str]) -> str:
        if not any(playlists_names):
            return ""
        favorite_list = [playlist_name for playlist_name in playlists_names if playlist_name.startswith("_")]
        if any(favorite_list):
            log.info("found a favorite playlist: %s", favorite_list[0])
            return get_playlist_id(favorite_list[0])
        log.info("a favorite playlist was not found, the first one in alphabetical order is chosen: %s", playlists_names[0])
        return get_playlist_id(playlists_names[0])

    def build_playlist_entries(playlists_names: List[str]) -> List[PlaylistEntry]:
        return [PlaylistEntry(name=get_playlist_name(playlist_name), id=get_playlist_id(playlist_name)) for playlist_name in playlists_names]

    log.info("building playlist index...")
    playlists_names: List[str] = [filename for filename in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, filename))]
    playlists_names.sort()
    log.info("found %d playlists folders", len(playlists_names))
    playlist_index: PlaylistIndex = PlaylistIndex(
        favorite=search_favorite_playlist(playlists_names),
        playlists=build_playlist_entries(playlists_names)
    )
    log.info("playlist index successfully built")
    return playlist_index


def build_playlist(input_dir: str, playlist_name: str) -> List[VideoEntry]:
    playlist_path = os.path.join(input_dir, playlist_name)
    files = os.listdir(playlist_path)
    files.sort()
    videos: List[VideoEntry] = []
    for filename in files:
        filepath = os.path.join(playlist_path, filename)
        if filename.endswith(".json") and not os.path.isdir(filepath):
            with open(filepath, "r") as fp:
                video: VideoEntry = VideoEntry(**json.load(fp))
                videos.append(video)
    return videos


def build(input_dir: str, output_dir: str) -> None:
    # first build the index file
    playlistindexpath = os.path.join(output_dir, "index")
    with open(playlistindexpath, "w") as fp:
        playlist_index: PlaylistIndex = build_playlist_index(input_dir)
        json.dump(asdict(playlist_index), fp)
    log.info("playlist index saved in %s", os.path.abspath(playlistindexpath))
    # then the playlists files
    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)
        if os.path.isdir(filepath):
            # if the playlist is the favorite one deletes the "_" prefix by the playlist name
            playlistname = filename[1:] if filename.startswith("_") else filename
            log.info("building playlist %s", playlistname)
            playlistpath = os.path.join(output_dir, get_playlist_id(playlistname))
            playlist = list(map(asdict, build_playlist(input_dir, filename)))
            with open(playlistpath, "w") as fp:
                json.dump(playlist, fp)
            log.info("playlist %s saved in %s", playlistname, os.path.abspath(playlistpath))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="IPlay4 CLI")
    parser.add_argument("-i", "--input", type=str, default=".", help="input directory")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-o", "--output", type=str, help="output directory", required=True)
    args = parser.parse_args()

    log.info("start processing playlists")
    try:
        build(args.input, args.output)
        log.info("done!")
    except:
        pass
