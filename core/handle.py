from core import internals

import logging
import yaml
import argparse

import os
import sys


_LOG_LEVELS_STR = ['INFO', 'WARNING', 'ERROR', 'DEBUG']

default_conf = { 'spotify-downloader':
                 { 'manual'                 : False,
                   'no-metadata'            : False,
                   'avconv'                 : False,
                   'folder'                 : os.path.join(sys.path[0], 'Music'),
                   'overwrite'              : 'prompt',
                   'input-ext'              : '.m4a',
                   'output-ext'             : '.mp3',
                   'download-only-metadata' : False,
                   'dry-run'                : False,
                   'music-videos-only'      : False,
                   'no-spaces'              : False,
                   'file-format'            : '{artist} - {track_name}',
                   'youtube-api-key'        : None,
                   'log-level'              : 'INFO' }
               }


def log_leveller(log_level_str):
    loggin_levels = [logging.INFO, logging.WARNING, logging.ERROR, logging.DEBUG]
    log_level_str_index = _LOG_LEVELS_STR.index(log_level_str)
    loggin_level = loggin_levels[log_level_str_index]
    return loggin_level


def merge(default, config):
    """ Override default dict with config dict. """
    merged = default.copy()
    merged.update(config)
    return merged


def get_config(config_file):
    try:
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
    except FileNotFoundError:
        with open(config_file, 'w') as ymlfile:
            yaml.dump(default_conf, ymlfile, default_flow_style=False)
            cfg = default_conf

    return cfg['spotify-downloader']


def override_config(config_file, parser, raw_args=None):
    """ Override default dict with config dict passed as comamnd line argument. """
    config_file = os.path.realpath(config_file)
    config = merge(default_conf['spotify-downloader'], get_config(config_file))

    parser.set_defaults(manual=config['manual'])
    parser.set_defaults(no_metadata=config['no-metadata'])
    parser.set_defaults(avconv=config['avconv'])
    parser.set_defaults(folder=os.path.relpath(config['folder'], os.getcwd()))
    parser.set_defaults(overwrite=config['overwrite'])
    parser.set_defaults(input_ext=config['input-ext'])
    parser.set_defaults(output_ext=config['output-ext'])
    parser.set_defaults(download_only_metadata=config['download-only-metadata'])
    parser.set_defaults(dry_run=config['dry-run'])
    parser.set_defaults(music_videos_only=config['music-videos-only'])
    parser.set_defaults(no_spaces=config['no-spaces'])
    parser.set_defaults(file_format=config['file-format'])
    parser.set_defaults(no_spaces=config['youtube-api-key'])
    parser.set_defaults(log_level=config['log-level'])

    return parser.parse_args(raw_args)


def get_arguments(raw_args=None, to_group=True, to_merge=True):
    parser = argparse.ArgumentParser(
        description='Download and convert songs from Spotify, Youtube etc.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    if to_merge:
        config_file = os.path.join(sys.path[0], 'config.yml')
        config = merge(default_conf['spotify-downloader'], get_config(config_file))
    else:
        config = default_conf['spotify-downloader']

    if to_group:
        group = parser.add_mutually_exclusive_group(required=True)

        group.add_argument(
            '-s', '--song', help='download song by spotify link or name')
        group.add_argument(
            '-l', '--list', help='download songs from a file')
        group.add_argument(
            '-p', '--playlist', help='load songs from playlist URL into <playlist_name>.txt')
        group.add_argument(
            '-b', '--album', help='load songs from album URL into <album_name>.txt')
        group.add_argument(
            '-u', '--username',
            help="load songs from user's playlist into <playlist_name>.txt")
        group.add_argument(
            '-st', '--savedtracks',
            help="load songs from user's saved tracks into saved_tracks.txt")

    parser.add_argument(
        '-m', '--manual', default=config['manual'],
        help='choose the song to download manually', action='store_true')
    parser.add_argument(
        '-nm', '--no-metadata', default=config['no-metadata'],
        help='do not embed metadata in songs', action='store_true')
    parser.add_argument(
        '-a', '--avconv', default=config['avconv'],
        help='Use avconv for conversion otherwise set defaults to ffmpeg',
        action='store_true')
    parser.add_argument(
        '-f', '--folder', default=os.path.relpath(config['folder'], os.getcwd()),
        help='path to folder where files will be stored in')
    parser.add_argument(
        '--overwrite', default=config['overwrite'],
        help='change the overwrite policy',
        choices={'prompt', 'force', 'skip'})
    parser.add_argument(
        '-i', '--input-ext', default=config['input-ext'],
        help='prefered input format .m4a or .webm (Opus)',
        choices={'.m4a', '.webm'})
    parser.add_argument(
        '-o', '--output-ext', default=config['output-ext'],
        help='prefered output format .mp3, .m4a (AAC), .flac, etc.')
    parser.add_argument(
        '-ff', '--file-format', default=config['file-format'],
        help='File format to save the downloaded song with, each tag '
             'is surrounded by curly braces. Possible formats: '
             '{}'.format([internals.formats[x] for x in internals.formats]),
        action='store_true')
    parser.add_argument(
        '-dm', '--download-only-metadata', default=config['download-only-metadata'],
        help='download songs for which metadata is found',
        action='store_true')
    parser.add_argument(
        '-d', '--dry-run', default=config['dry-run'],
        help='Show only track title and YouTube URL',
        action='store_true')
    parser.add_argument(
        '-mo', '--music-videos-only', default=config['music-videos-only'],
        help='Search only for music on Youtube',
        action='store_true')
    parser.add_argument(
        '-ns', '--no-spaces', default=config['no-spaces'],
        help='Replace spaces with underscores in file names',
        action='store_true')
    parser.add_argument(
        '-ll', '--log-level', default=config['log-level'],
        choices=_LOG_LEVELS_STR,
        type=str.upper,
        help='set log verbosity')
    parser.add_argument(
        '-yk', '--youtube-api-key', default=config['youtube-api-key'],
        help=argparse.SUPPRESS)
    parser.add_argument(
        '-c', '--config', default=None,
        help='Replace with custom config.yml file')

    parsed = parser.parse_args(raw_args)

    if parsed.config is not None and to_merge:
        parsed = override_config(parsed.config, parser)

    parsed.log_level = log_leveller(parsed.log_level)

    return parsed
