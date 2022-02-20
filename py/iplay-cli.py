#!/usr/bin/env python3
import logging

import coloredlogs

import command
import http_server
import iplay_processor

__author__ = "Simone Pandolfi <simopandolfi@gmail.com>"
__version__ = (1, 0, 0, "benjamino")

log_level = logging.INFO
log_format = "%(asctime)s [%(process)d] %(levelname)s %(message)s"
coloredlogs.install(level=log_level, fmt=log_format)
log = logging.getLogger()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="IPlay4 CLI")
    subparsers = parser.add_subparsers(dest="schema")

    http_parser = subparsers.add_parser("http", help="HTTP schema")
    http_server.load_parser(http_parser)

    playlists_parser = subparsers.add_parser("playlists", help="Playlists schema")
    iplay_processor.load_parser(playlists_parser)

    args = parser.parse_args()

    schema = args.schema
    cmd = args.cmd
    command.SCHEMA[schema][cmd](**args.__dict__)
