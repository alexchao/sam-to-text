# -*- coding: utf-8 -*-
import json
from collections import namedtuple
import os
import re


RE_FILE_EXT = re.compile('.*\.(json|html)')


class TranscriptConfig(namedtuple(
    'TranscriptConfig',
    ['id', 'title', 'source_files']
)):

    @property
    def source_type(self):
        first_file = self.source_files[0]
        match = re.search(RE_FILE_EXT, first_file)
        if not match:
            raise Exception('Unexpected file type: {}'.format(first_file))

        return match.group(1).upper()


def make_relative_paths(source_files, path_head):
    """Script location might be different from config/transcript location."""
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

