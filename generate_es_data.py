# -*- coding: utf-8 -*-
import argparse
import json
import logging

from bs4 import BeautifulSoup

from sam_to_text.processors.transcript_chunker import TranscriptChunker
from sam_to_text.processors.gcs import process_gcs_transcript
from sam_to_text.processors.watson import process_watson_transcript
from sam_to_text.transcript_config import ConfigType
from sam_to_text.transcript_config import read_config


logging.basicConfig(level=logging.INFO)


def htmlify_chunk(chunk, index):
    return '<div class="chunk" id="chunk-{id}">{chunk}</div>'.format(
        id=index, chunk=chunk)


def write_html_document(full_html, config, html_path):
    with open('template.html', 'r') as template_file:
        template_html = template_file.read()

    html_document = template_html.format(
        title=config.title,
        content=full_html)
    html_file_path = '{html_path}{doc_id}.html'.format(
        html_path=html_path,
        doc_id=config.id)
    with open(html_file_path, 'w') as out_html_file:
        out_html_file.write(html_document)


def write_es_document(chunk, index, config, es_path):
    json_doc = {
        'id': config.id,
        'title': config.title,
        'chunk_id': index,
        'content': chunk
    }
    es_file_path = '{es_path}{doc_id}-{i}.json'.format(
        es_path=es_path,
        doc_id=config.id,
        i=index)
    with open(es_file_path, 'w') as out_es_file:
        out_es_file.write(json.dumps(json_doc))


def process_transcript(config, html_path, es_path):
    """Given a transcript config, generate the HTML file and ES documents
    and write them to disk.
    """
    logging.info('Processing transcript {}, with files...'.format(config.id))
    for file_path in config.source_files:
        logging.info('    {}'.format(file_path))
    if config.type == ConfigType.GCS:
        chunks = process_gcs_transcript(config)
    elif config.type == ConfigType.WATSON:
        chunks = process_watson_transcript(config)
    elif config.type == ConfigType.HTML:
        if len(config.source_files) > 1:
            raise Exception('Encountered multiple files for HTML transcript.')
        chunks = process_html_transcript(config)

    full_html = ''
    for index, chunk in enumerate(chunks):
        write_es_document(chunk.raw, index, config, es_path)
        full_html += htmlify_chunk(chunk.html, index)

    write_html_document(full_html, config, html_path)


def process_html_transcript(config):
    """Process a transcript that's already in HTML format."""
    file_path = config.source_files[0]
    with open(file_path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    chunker = TranscriptChunker()
    for el in soup.contents:
        if el.name == 'p':
            # soup.text strips all tags
            chunker.add_transcript(el.text, '<p>{}</p>'.format(el.text))

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
