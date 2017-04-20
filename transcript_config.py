# -*- coding: utf-8 -*-
import json
from collections import namedtuple
import os


TranscriptConfig = namedtuple(
    'TranscriptConfig',
    ['id', 'title', 'source_files']
)


def make_relative_paths(source_files, path_head):
    return [
        os.path.join(path_head, file_path)
        for file_path in source_files
    ]


def read_config(file_path):
    head, _ = os.path.split(file_path)
    with open(file_path, 'r') as f:
        json_data = json.loads(f.read())
    return [
        TranscriptConfig(
            transcript_json['id'],
            transcript_json['title'],
            make_relative_paths(transcript_json['source_files'], head)
        )
        for transcript_json in json_data['transcripts']
    ]

