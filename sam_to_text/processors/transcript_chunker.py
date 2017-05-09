# -*- coding: utf-8 -*-
from collections import namedtuple


# Max length of a transcript chunk in characters
CHUNK_MAX_LENGTH = 1024


FormattedChunk = namedtuple('FormattedChunk', ['raw', 'html'])


class TranscriptChunker:
    """Allows text to be chunked according to CHUNK_MAX_LENGTH. This is
    to allow breaking up a single large document into a set of smaller
    documents for ES ingestion.

    Accumulates a list of `FormattedChunk`s.
    """

    def __init__(self, max_length=None):
        self._max_length = max_length or CHUNK_MAX_LENGTH
        self._chunk_length = 0
        self._chunk_raw = []
        self._chunk_html = []
        self._chunks = []

    def add_transcript(self, raw, html):
        self._chunk_raw.append(raw)
        self._chunk_html.append(html)
        self._chunk_length += len(raw)
        if self._chunk_length > self._max_length:
            self._chunks.append(self._freeze_chunk())
            self._chunk_length = 0
            self._chunk_raw = []
            self._chunk_html = []

    def get_chunks(self):
        if self._chunk_length > 0:
            return self._chunks + [self._freeze_chunk()]
        return self._chunks

    def _freeze_chunk(self):
        return FormattedChunk(
            ' '.join(self._chunk_raw),
            ''.join(self._chunk_html)
        )
