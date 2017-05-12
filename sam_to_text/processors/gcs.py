# -*- coding: utf-8 -*-
import json

from sam_to_text.processors.transcript_chunker import TranscriptChunker


def process_gcs_transcript(config):
    """Process a Google Cloud Speech transcript."""
    chunker = TranscriptChunker()
    for file_path in config.source_files:
        with open(file_path, 'r') as f:
            result_json = json.loads(f.read())

        results = result_json['results']
        for result in results:
            best_transcript = get_best_transcript_from_result(result)
            chunker.add_transcript(
                best_transcript,
                '<p>{}</p>'.format(best_transcript))

    return chunker.get_chunks()


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
