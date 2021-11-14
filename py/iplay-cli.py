#!/usr/bin/env python3
import argparse
import json
import logging
from typing import Any, Dict, List
import os

import coloredlogs

__author__ = "Simone Pandolfi <simopandolfi@gmail.com>"
__version__ = (1, 0, 0, "salamandra")

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type=str, default=".", help="input directory")
parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
parser.add_argument("-vv", "--very-verbose", action="store_true", help="very verbose output")
requiredNamed = parser.add_argument_group('required arguments')
requiredNamed.add_argument("-o", "--output", type=str, help="output directory", required=True)
args = parser.parse_args()

log_level = logging.INFO if args.verbose or args.very_verbose else logging.FATAL
log_format = "%(asctime)s [%(process)d] %(levelname)s %(message)s" if args.very_verbose else "%(message)s"
coloredlogs.install(level=log_level, fmt=log_format)
log = logging.getLogger()


def get_playlist_id(playlist_name: str) -> str:
    return playlist_name.lower().replace(" ", "-")


def build_playlist_index(input_dir: str) -> Dict[str, Any]:
    log.info("building playlist index...")
    playlist_index = {
        "favorite": "",
        "playlists": [],
    }
    playlists_dirs = [filename for filename in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, filename))]
    log.info("found %d playlists folders", len(playlists_dirs))
    for filename in playlists_dirs:
        log.info("processing: %s", filename)
        playlist_id = get_playlist_id(filename)
        # the underscore ("_") character as first one of the playlist name indicates the favorite playlist
        if filename.startswith("_"):
            filename = filename[1:]
            playlist_id = get_playlist_id(filename)
            playlist_index["favorite"] = playlist_id
            log.info("found favorite playlist: %s", filename)
        playlist_index["playlists"].append({
            "name": filename,
            "id": playlist_id,
            "url": f'/playlists/{playlist_id}',
        })
    playlist_index["playlists"] = sorted(playlist_index["playlists"], key=lambda pl: pl["name"])
    log.info("playlist index successfully built")
    return playlist_index


def build_playlist(input_dir: str, playlist_name: str) -> List[Dict[str, str]]:
    videos = []
    playlist_path = os.path.join(input_dir, playlist_name)
    files = os.listdir(playlist_path)
    files.sort()
    for filename in files:
        filepath = os.path.join(playlist_path, filename)
        if filename.endswith(".json") and not os.path.isdir(filepath):
            with open(filepath, "r") as fp:
                videos.append(json.load(fp))
    return videos


def build(input_dir: str, output_dir: str) -> None:
    # first build the index file
    playlistindexpath = os.path.join(output_dir, "index")
    with open(playlistindexpath, "w") as fp:
        playlist_index = build_playlist_index(input_dir)
        json.dump(playlist_index, fp)
    log.info("playlist index saved in %s", os.path.abspath(playlistindexpath))
    # then the playlists files
    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)
        if os.path.isdir(filepath):
            # if the playlist is the favorite one deletes the "_" prefix by the playlist name
            playlistname = filename[1:] if filename.startswith("_") else filename
            log.info("building playlist %s", playlistname)
            playlistpath = os.path.join(args.output, get_playlist_id(playlistname))
            with open(playlistpath, "w") as fp:
                playlist = build_playlist(input_dir, filename)
                json.dump(playlist, fp)
            log.info("playlist %s saved in %s", playlistname, os.path.abspath(playlistpath))


if __name__ == '__main__':
    log.info("start processing playlists")
    try:
        build(args.input, args.output)
        log.info("done!")
    except:
        pass
