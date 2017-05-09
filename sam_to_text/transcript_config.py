# -*- coding: utf-8 -*-
from enum import Enum
import json
from collections import namedtuple
import os


class ConfigType(Enum):
    """Types of configs supported.
    GCS: Google Cloud Speech JSON
    WATSON: IBM Watson Speech-To-Text JSON
    HTML: Raw HTML file with text wrapped in paragraph tags.
    """
    GCS = 'api/gcs'
    WATSON = 'api/watson'
    HTML = 'html'


TranscriptConfig = namedtuple(
    'TranscriptConfig',
    ['id', 'type', 'title', 'source_files']
)


def make_relative_paths(source_files, path_head):
    """Script location might be different from config/transcript location."""
    return [
        os.path.join(path_head, file_path)
        for file_path in source_files
    ]


def read_config(file_path):
    """Given a file path to a transcript config file, return a list of
    TranscriptConfig's.
    """
    head, _ = os.path.split(file_path)
    with open(file_path, 'r') as f:
        json_data = json.loads(f.read())
    return [
        TranscriptConfig(
            transcript_json['id'],
            ConfigType(transcript_json['type']),
            transcript_json['title'],
            make_relative_paths(transcript_json['source_files'], head)
        )
        for transcript_json in json_data['transcripts']
    ]
