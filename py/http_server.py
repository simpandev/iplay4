#!/usr/bin/env python3
import argparse
from collections import namedtuple
from enum import Enum
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
import signal
from typing import BinaryIO, Union

import coloredlogs

from command import command

__author__ = "Simone Pandolfi <simopandolfi@gmail.com>"
__version__ = (1, 0, 0, "prugno")

MimeType = namedtuple("MimeType", ["extension", "mime_type"])

coloredlogs.install(level=logging.INFO)
log = logging.getLogger()

BASE_PATH: Union[str, None] = os.path.abspath(os.path.dirname(__file__))


def get_absolute_filepath(url_path: str) -> str:
    """
    Transform a URL path into a filesystem path.
    
    :param url_path: URL relative path
    :returns: the absolute path referring to the resource in the filesystem
    """
    path = url_path.replace("/", os.sep)
    resource_path = os.path.join(BASE_PATH, path)
    if resource_path.endswith(os.sep):
        resource_path = resource_path[:-1]
    return resource_path


class HttpResponseStatusEnum(Enum):
    OK = 200
    NOT_FOUND = 404


class MimeTypeEnum(Enum):
    TEXT_PLAIN = MimeType(None, "text/plain")
    HTML = MimeType("html", "text/html")
    CSS = MimeType("css", "text/css")
    JS = MimeType("js", "text/javascript")
    JSON = MimeType("json", "application/json")
    PNG = MimeType("png", "image/png")
    SVG = MimeType("svg", "image/svg+xml")


class AngularServer(BaseHTTPRequestHandler):

    def do_GET(self):
        local_path = get_absolute_filepath(self.path[1:])
        if self.path.startswith("/playlists"):
            if os.path.exists(local_path):
                self.__playlist(local_path)
            else:
                self.__not_found()
        else:
            if local_path == BASE_PATH or not os.path.exists(local_path):
                self.__index()
            else:
                self.__resource(local_path)
    
    def __send(self, status: HttpResponseStatusEnum, content_type: MimeTypeEnum, payload: Union[str, BinaryIO]) -> None:
        if hasattr(payload, 'read'):
            body = payload.read()
        else:
            body = bytes(payload, "utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", content_type.value.mime_type)
        self.send_header("Length", len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def __not_found(self) -> None:
        self.__send(HttpResponseStatusEnum.NOT_FOUND, MimeTypeEnum.TEXT_PLAIN, "404 - Not Found")

    def __playlist(self, local_path: str) -> None:
        with open(local_path, "rb") as fp:
            self.__send(HttpResponseStatusEnum.OK, MimeTypeEnum.JSON, fp)
    
    def __index(self) -> None:
        index_filepath = os.path.join(BASE_PATH, "index.html")
        with open(index_filepath, "rb") as fp:
            self.__send(HttpResponseStatusEnum.OK, MimeTypeEnum.HTML, fp)
    
    def __resource(self, local_path: str) -> None:
        with open(local_path, "rb") as fp:
            for mime_type_enum in MimeTypeEnum:
                if mime_type_enum.value.extension is not None and local_path.endswith(f".{mime_type_enum.value.extension}"):
                    mime = mime_type_enum
                    break
            else:
                mime = MimeTypeEnum.TEXT_PLAIN
            self.__send(HttpResponseStatusEnum.OK, mime, fp)


def start_server(bind: str, port: int, directory: str) -> None:
    global BASE_PATH
    BASE_PATH = os.path.abspath(directory)

    web_server = HTTPServer((bind, port), AngularServer)
    log.info("server binded to address %s", bind)
    log.info("server listening on port %d", port)
    log.info("server started!")

    signal.signal(signal.SIGTERM, lambda: web_server.shutdown())
    signal.signal(signal.SIGKILL, lambda: web_server.shutdown())

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        web_server.shutdown()
        log.info("server stopped.")


def load_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("cmd", type=str, choices=("start",), help="Command")
    parser.add_argument("-d", "--directory", type=str, default=".", help="Specify alternative directory [default:current directory]")
    parser.add_argument("-b", "--bind", type=str, default="localhost", help="Specify alternate bind address [default: localhost]")
    parser.add_argument("port", type=int, default=8000, nargs="?", action="store", help="Specify alternate port [default: 8000]")


@command(schema="http", cmd="start")
def http_start(**kwargs) -> None:
    start_server(kwargs["bind"], kwargs["port"], kwargs["directory"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple HTTP server to serve an Angular SPA (Single Page Application).")
    load_parser(parser)
    args = parser.parse_args()

    start_server(args.bind, args.port, args.directory)
