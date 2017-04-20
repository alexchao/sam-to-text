# -*- coding: utf-8 -*-
import argparse
import json

from transcript_config import read_config


STATIC_BASE_URI = 'https://storage.googleapis.com/sam-to-text-html/'

# Max length of a transcript chunk in characters
CHUNK_MAX_LENGTH = 5000


def make_static_uri(doc_id):
    return STATIC_BASE_URI + doc_id + '.html'


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


def write_html_document(chunks, config, html_path):
    with open('template.html', 'r') as template_file:
        template_html = template_file.read()

    full_html = ''.join(chunks)
    html_document = template_html.format(
        title=config.title,
        content=full_html)
    html_file_path = '{html_path}{doc_id}.html'.format(
        html_path=html_path,
        doc_id=config.id)
    with open(html_file_path, 'w') as out_html_file:
        out_html_file.write(html_document)


def write_es_documents(chunks, config, es_path):
    for i, chunk in enumerate(chunks):
        json_doc = {
            'id': config.id,
            'static_uri': make_static_uri(config.id),
            'title': config.title,
            'chunk_id': i,
            'total_chunks': len(chunks),
            'content': chunk
        }
        es_file_path = '{es_path}{doc_id}-{i}.json'.format(
            es_path=es_path,
            doc_id=config.id,
            i=i)
        with open(es_file_path, 'w') as out_es_file:
            out_es_file.write(json.dumps(json_doc))


def process_transcript(config, html_path, es_path):
    """Given a transcript config, generate the HTML file and ES documents
    and write them to disk.
    """
    chunker = TranscriptChunker()
    for file_path in config.source_files:
        with open(file_path, 'r') as f:
            result_json = json.loads(f.read())

        results = result_json['results']
        for result in results:
            best_transcript = get_best_transcript_from_result(result)
            chunker.add_transcript('<p>{}</p>'.format(best_transcript))

    all_chunks = chunker.get_chunks()
    write_html_document(all_chunks, config, html_path)
    write_es_documents(all_chunks, config, es_path)


def process_transcripts(config_path, html_path, es_path):
    """Read the transcript config file and generate HTML documents
    and ES documents for each transcript."""
    configs = read_config(config_path)
    for config in configs:
        process_transcript(config, html_path, es_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_path', help='File path to transcript config')
    parser.add_argument('html_path', help='HTML directory output path')
    parser.add_argument('es_path', help='ES document directory output path')
    args = parser.parse_args()
    process_transcripts(args.config_path, args.html_path, args.es_path)
