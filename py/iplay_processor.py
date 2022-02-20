#!/usr/bin/env python3
from argparse import ArgumentParser
from collections import namedtuple
from dataclasses import dataclass, asdict, field
from datetime import timedelta, datetime
from email.mime import base
import json
import logging
from pathlib import Path
import re
from typing import List, Optional, Union
import os

import coloredlogs

from command import command

__author__ = "Simone Pandolfi <simopandolfi@gmail.com>"
__version__ = (1, 0, 0, "salamandra")

log_level = logging.INFO
log_format = "%(asctime)s [%(process)d] %(levelname)s %(message)s"
coloredlogs.install(level=log_level, fmt=log_format)
log = logging.getLogger()


PADDING = 7


FilenameInfo = namedtuple("FilenameInfo", ["index", "video_id"])


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
    file_index: Optional[int] = None

    def save(self, dir_path: Union[str, Path]) -> "VideoEntry":
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise ValueError(f"directory does not exists, got {dir_path}")
        if self.file_index is None:
            file_count = sum(map(lambda f: 1, dir_path.glob("*.json")))
            self.file_index = VideoEntry.build_new_index(file_count)
        filepath = Path(dir_path, self.filename)
        with open(filepath, "w") as fp:
            content = {k: v for k, v in asdict(self).items() if k != "file_index"}
            json.dump(content, fp, indent=True, default=str)
        return self
    
    @property
    def filename(self) -> str:
        if self.file_index is None:
            raise ValueError(f"unknown file index")
        return VideoEntry.build_filename(self.file_index, self.video_id)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "VideoEntry":
        filepath = Path(path)
        if not filepath.exists():
            raise ValueError(f"unknown video file, got {filepath}")
        with open(filepath, "r") as fp:
            buff = json.load(fp)
        instance = cls(**buff)
        file_index = VideoEntry.extract_filename_info(filepath.name).index
        instance.file_index = file_index
        return instance
    
    @staticmethod
    def build_filename(file_index: int, video_id: str) -> str:
        return f"{str(file_index).zfill(PADDING)}__{video_id}.json"
    
    @staticmethod
    def extract_filename_info(filepath: str) -> FilenameInfo:
        path = Path(filepath)
        matcher = re.match(r"^(?P<file_index>\d+)__(?P<video_id>[\w\-]+).json$", path.name)
        if matcher is None:
            raise ValueError(f"Not a video file, got {filepath}")
        return FilenameInfo(*matcher.groups())
    
    @staticmethod
    def build_new_index(x: int) -> int:
        return 10 + x * 10


class Compiler:

    def compile(self, input_dir: str, output_dir: str) -> None:
        log.info("start processing playlists")
        # first build the index file
        playlistindexpath = os.path.join(output_dir, "index")
        with open(playlistindexpath, "w") as fp:
            playlist_index: PlaylistIndex = self.__compile_index(input_dir)
            json.dump(asdict(playlist_index), fp)
        log.info("playlist index saved in %s", os.path.abspath(playlistindexpath))
        # then the playlists files
        for filename in os.listdir(input_dir):
            filepath = os.path.join(input_dir, filename)
            if os.path.isdir(filepath):
                # if the playlist is the favorite one deletes the "_" prefix by the playlist name
                playlistname = filename[1:] if filename.startswith("_") else filename
                log.info("building playlist %s", playlistname)
                playlistpath = os.path.join(output_dir, self.__get_playlist_id(playlistname))
                playlist = list(map(asdict, self.__compile_playlist(input_dir, filename)))
                with open(playlistpath, "w") as fp:
                    json.dump(playlist, fp)
                log.info("playlist %s saved in %s", playlistname, os.path.abspath(playlistpath))
        log.info("done!")

    def __compile_index(self, input_dir: str) -> PlaylistIndex:

        def search_favorite_playlist(playlists_names: List[str]) -> str:
            if not any(playlists_names):
                return ""
            favorite_list = [playlist_name for playlist_name in playlists_names if playlist_name.startswith("_")]
            if any(favorite_list):
                log.info("found a favorite playlist: %s", favorite_list[0])
                return self.__get_playlist_id(favorite_list[0])
            log.info("a favorite playlist was not found, the first one in alphabetical order is chosen: %s", playlists_names[0])
            return self.__get_playlist_id(playlists_names[0])

        def build_playlist_entries(playlists_names: List[str]) -> List[PlaylistEntry]:
            return [PlaylistEntry(name=self.__get_playlist_name(playlist_name), id=self.__get_playlist_id(playlist_name)) for playlist_name in playlists_names]

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

    def __compile_playlist(self, input_dir: str, playlist_name: str) -> List[VideoEntry]:
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
    
    def __get_playlist_id(self, playlist_name: str) -> str:
        name = playlist_name[1:] if playlist_name.startswith("_") else playlist_name
        return name.lower().replace(" ", "-")
    
    def __get_playlist_name(self, playlist_name: str) -> str:
        return playlist_name[1:] if playlist_name.startswith("_") else playlist_name


def archive_reallocation(archive_dir: Union[str, Path]) -> None:
    archive_dir = Path(archive_dir)
    for playlist_dir in archive_dir.iterdir():
        if not playlist_dir.is_dir():
            continue
        playlist_name = playlist_dir.name if not playlist_dir.name.startswith("_") else playlist_dir.name[1:]
        log.info("reallocating '%s'", playlist_name)
        videos: List[Path] = sorted(list(playlist_dir.glob("*.json")))
        for index, video_filepath in enumerate(videos):
            new_index = VideoEntry.build_new_index(index)
            video_id = VideoEntry.extract_filename_info(video_filepath).video_id
            video_filename = VideoEntry.build_filename(new_index, video_id)
            new_filepath = Path(playlist_dir, video_filename)
            os.rename(video_filepath, new_filepath)


def create_new_video_entry(archive_dir: Union[str, Path], playlist: str, title: str, author: str, duration: timedelta, video_id: str) -> None:
    playlist_dir = Path(archive_dir, f"_{playlist}")
    if not playlist_dir.exists():
        playlist_dir = Path(archive_dir, playlist)
        if not playlist_dir.exists():
            raise ValueError(f"unknown playlist, got '{playlist}'")
    video = VideoEntry(title=title, author=author, duration=duration, video_id=video_id)
    video.save(playlist_dir)
    log.info("created new video entry: %s - %s", title, author)


def update_video_entry(archive_dir: Union[str, Path], playlist: str, old_video_id: str, new_video_id: str, duration: Optional[timedelta]) -> None:
    playlist_dir = Path(archive_dir, f"_{playlist}")
    if not playlist_dir.exists():
        playlist_dir = Path(archive_dir, playlist)
        if not playlist_dir.exists():
            raise ValueError(f"unknown playlist, got '{playlist}'")
    files = list(playlist_dir.glob(f"*__{old_video_id}.json"))
    if not any(files):
        raise ValueError(f"unknown video ID, got '{old_video_id}'")
    filepath = files[0]
    video_entry = VideoEntry.load(filepath)
    video_entry.video_id = new_video_id
    if duration is not None:
        video_entry.duration = duration
    video_entry.save(playlist_dir)
    new_filepath = Path(playlist_dir, video_entry.filename)
    os.rename(filepath, new_filepath)


def load_parser(parser: ArgumentParser) -> None:

    def mktime(s: str) -> timedelta:
        return datetime.strptime(s, "%H:%M:%S").time()
    
    def add_compile_command(subparsers) -> None:
        parser = subparsers.add_parser("compile", help="Compile playlists")
        parser.add_argument("-i", "--input", type=str, default=".", help="input directory")
        parser.add_argument("output", type=str, help="output directory")
    
    def add_reallocate_command(subparsers) -> None:
        parser = subparsers.add_parser("reallocate", help="Reallocate the archive")
        parser.add_argument("archive_dir", type=str, help="Archive directory")
    
    def add_create_video_command(subparsers) -> None:
        parser = subparsers.add_parser("create", help="Create new video entry")
        parser.add_argument("archive_dir", type=str, help="Archive directory")
        parser.add_argument("playlist", type=str, help="Playlist name")
        parser.add_argument("title", type=str, help="Video title")
        parser.add_argument("author", type=str, help="Author name")
        parser.add_argument("duration", type=mktime, help="Video duration")
        parser.add_argument("video_id", type=str, help="Video ID")
    
    def add_update_video_command(subparsers) -> None:
        parser = subparsers.add_parser("update", help="Update video entry")
        parser.add_argument("archive_dir", type=str, help="Archive directory")
        parser.add_argument("playlist", type=str, help="Playlist name")
        parser.add_argument("old_video_id", type=str, help="Old video ID")
        parser.add_argument("new_video_id", type=str, help="New video ID")
        parser.add_argument("-d", "--duration", type=mktime, help="Video duration")

    subparsers = parser.add_subparsers(dest="cmd")
    add_compile_command(subparsers)
    add_reallocate_command(subparsers)
    add_create_video_command(subparsers)
    add_update_video_command(subparsers)


@command(schema="playlists", cmd="compile")
def compile_playlists_command(**kwargs) -> None:
    Compiler().compile(kwargs["input"], kwargs["output"])


@command(schema="playlists", cmd="reallocate")
def reallocate_playlist_entries(**kwargs) -> None:
    archive_reallocation(kwargs["archive_dir"])


@command(schema="playlists", cmd="create")
def create_new_video(**kwargs) -> None:
    create_new_video_entry(kwargs["archive_dir"], kwargs["playlist"], kwargs["title"], kwargs["author"], kwargs["duration"], kwargs["video_id"])


@command(schema="playlists", cmd="update")
def update_video(**kwargs) -> None:
    update_video_entry(kwargs["archive_dir"], kwargs["playlist"], kwargs["old_video_id"], kwargs["new_video_id"], kwargs["duration"])


if __name__ == '__main__':
    parser = ArgumentParser(description="IPlay4 PROCESSOR")
    load_parser(parser)
    args = parser.parse_args()

    cmd = args.cmd
    kwargs = args.__dict__
    if cmd == "compile":
        compile_playlists_command(**kwargs)
    elif cmd == "reallocate":
        reallocate_playlist_entries(**kwargs)
    elif cmd == "create":
        create_new_video(**kwargs)
    elif cmd == "update":
        update_video(**kwargs)
    else:
        raise ValueError(f"unknown command: {cmd}")
