# -*- coding: utf-8 -*-
import argparse
import json
import logging

from bs4 import BeautifulSoup

from transcript_config import read_config


logging.basicConfig(level=logging.INFO)


STATIC_BASE_URI = 'https://storage.googleapis.com/sam-to-text-html/'

# Max length of a transcript chunk in characters
CHUNK_MAX_LENGTH = 1000


def make_static_uri(doc_id):
    return STATIC_BASE_URI + doc_id + '.html'


def htmlify_chunks(chunks):
    html_chunks = []
    for i, chunk in enumerate(chunks):
        html_chunks.append(
            '<div class="chunk" id="chunk-{id}">{chunk}</div>'.format(
                id=i, chunk=chunk))
    return html_chunks


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
    logging.info('Processing transcript {}, with files...'.format(config.id))
    for file_path in config.source_files:
        logging.info('    {}'.format(file_path))
    if config.source_type == 'JSON':
        chunks = process_gcs_transcript(config)
    elif config.source_type == 'HTML':
        if len(config.source_files) > 1:
            raise Exception('Encountered multiple files for HTML transcript.')
        chunks = process_html_transcript(config)

    html_chunks = htmlify_chunks(chunks)
    write_html_document(html_chunks, config, html_path)
    write_es_documents(html_chunks, config, es_path)


def process_html_transcript(config):
    """Process a transcript that's already in HTML format."""
    file_path = config.source_files[0]
    with open(file_path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    chunker = TranscriptChunker()
    for el in soup.contents:
        if el.name == 'p':
            chunker.add_transcript('<p>{}</p>'.format(el.text))

    return chunker.get_chunks()


def process_gcs_transcript(config):
    """Process a Google Cloud Speech transcript."""
    chunker = TranscriptChunker()
    for file_path in config.source_files:
        with open(file_path, 'r') as f:
            result_json = json.loads(f.read())

        results = result_json['results']
        for result in results:
            best_transcript = get_best_transcript_from_result(result)
            chunker.add_transcript('<p>{}</p>'.format(best_transcript))

    return chunker.get_chunks()


def process_transcripts(config_path, html_path, es_path):
    """Read the transcript config file and generate HTML documents
    and ES documents for each transcript.
    """
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
