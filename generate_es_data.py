# -*- coding: utf-8 -*-
import argparse
import json

from util import get_id_and_title_from_file_path


# Max length of a transcript chunk in characters
CHUNK_MAX_LENGTH = 5000


class TranscriptChunker:
    """Allows text to be chunked according to CHUNK_MAX_LENGTH. This is
    to allow breaking up a single large document into a set of smaller
    documents for ES ingestion.
    """

    def __init__(self):
        self._chunk = ''
        self._chunks = []

    def add_transcript(self, text):
        self._chunk += text
        if len(self._chunk) > CHUNK_MAX_LENGTH:
            self._chunks.append(self._chunk)
            self._chunk = ''

    def get_chunks(self):
        if self._chunk:
            return self._chunks + [self._chunk]
        return self._chunks


def get_best_transcript_from_result(result):
    """Use confidence level to determine the best transcript among all
    alternatives.
    """
    best_transcript = None
    best_confidence = -1
    for a in result['alternatives']:
        if a['confidence'] > best_confidence:
            best_transcript = a['transcript']
            best_confidence = a['confidence']
    return best_transcript


def process_transcript(in_file_path, html_path, es_path):
    """Make an HTML web page out of a Google Cloud Speech json file."""
    doc_id, title = get_id_and_title_from_file_path(in_file_path)

    with open(in_file_path, 'r') as f:
        result_json = json.loads(f.read())

    with open('template.html', 'r') as template_file:
        template_html = template_file.read()

    results = result_json['results']
    chunker = TranscriptChunker()
    for result in results:
        best_transcript = get_best_transcript_from_result(result)
        chunker.add_transcript('<p>{}</p>'.format(best_transcript))

    all_chunks = chunker.get_chunks()
    full_html = ''.join(all_chunks)
    html_document = template_html.format(title=title, content=full_html)
    html_file_path = '{html_path}{doc_id}.html'.format(
        html_path=html_path,
        doc_id=doc_id)
    with open(html_file_path, 'w') as out_html_file:
        out_html_file.write(html_document)

    for i, chunk in enumerate(all_chunks):
        json_doc = {
            'id': doc_id,
            'title': title,
            'chunk_id': i,
            'total_chunks': len(all_chunks),
            'content': chunk
        }
        es_file_path = '{es_path}{doc_id}-{i}.json'.format(
            es_path=es_path,
            doc_id=doc_id,
            i=i)
        with open(es_file_path, 'w') as out_es_file:
            out_es_file.write(json.dumps(json_doc))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_paths', help='Paths to Google Cloud Speech output')
    parser.add_argument('html_path', help='HTML directory path')
    parser.add_argument('es_path', help='ES document directory path')
    args = parser.parse_args()
    all_paths = args.in_paths.split(',')
    for path in all_paths:
        process_transcript(path, args.html_path, args.es_path)
