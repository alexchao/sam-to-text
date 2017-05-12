# -*- coding: utf-8 -*-
import json

from sam_to_text.processors.transcript_chunker import TranscriptChunker


def validate_result_status(result, result_transcript):
    """Check to make sure result meets expected conditions for processing.
    That is, there should only be one alternative, and all results should be
    labeled "final."

    Arguments:
    result -- result JSON
    result_transcript -- transcript text for error messaging

    """
    if len(result['alternatives']) > 1:
        raise Exception('Found > 1 alternatives for result: {}'.format(
            result_transcript))
    if not result['final']:
        raise Exception('Found non-final result: {}'.format(
            result_transcript))


def process_watson_transcript(config):
    """Process a transcript generated by the IBM Watson speech recognize API.
    """
    chunker = TranscriptChunker()

    # TODO: don't assume 1 file
    file_path = config.source_files[0]
    with open(file_path, 'r') as f:
        result_json = json.loads(f.read())

    speaker_labels = {
        label['from']: label for label in result_json['speaker_labels']
    }

    for result in result_json['results']:
        best_result = result['alternatives'][0]
        validate_result_status(result, best_result['transcript'])
        transcript_html = make_html_from_result(
            best_result,
            config,
            speaker_labels)
        chunker.add_transcript(best_result['transcript'], transcript_html)

    return chunker.get_chunks()


def group_utterances_by_speaker(timestamps, word_confidence, speaker_labels):
    """Given timestamp information for a transcript, group the words into
    phrases according to who spoke them. Also, for convenience, merge in
    word_confidence info.

    Arguments:
    timestamps -- list of ["word", 1.56, 1.89]
    word_confidence -- list of ["word", 0.9]
    speaker_labels -- dict mapping "from" timestamp to speaker label

    Return a list of {'speaker_id', 'utterances' (list)} objects, where
        an `utterance` is a {'word', 'confidence'} object.
    """
    dialogue = []
    speaker_id = None
    utterances = []
    for i, timestamp in enumerate(timestamps):
        utterance, ts_from, _ = timestamp
        new_speaker_id = speaker_labels[ts_from]['speaker']
        if speaker_id is None:
            speaker_id = new_speaker_id
        elif speaker_id != new_speaker_id:
            dialogue.append({'speaker_id': speaker_id, 'utterances': utterances})
            speaker_id = new_speaker_id
            utterances = []

        if timestamp[0] != word_confidence[i][0]:
            raise Exception(
                'Found timestamp-word_confidence mismatch: {}'.format(
                    timestamp[0] + ' =/= ' + word_confidence[i][0]))

        utterances.append({
            'word': timestamp[0],
            'confidence': word_confidence[i][1]
        })

    dialogue.append({'speaker_id': speaker_id, 'utterances': utterances})
    return dialogue


def make_html_from_result(result, config, speaker_labels):
    dialogue = group_utterances_by_speaker(
        result['timestamps'],
        result['word_confidence'],
        speaker_labels)

    full_html = ''
    for speech in dialogue:
        speaker_name = get_speaker_name(config, speech['speaker_id'])
        words = []
        for utterance in speech['utterances']:
            template = get_word_template(utterance['confidence'])
            words.append(template.format(w=utterance['word']))

        full_html += '<p><span class="speaker-name">{speaker}</span>: {words}</p>'.format(
            speaker=speaker_name,
            words=' '.join(words))

    return full_html


def get_word_template(confidence_level):
    if confidence_level < 0.2:
        return '<span class="confidence-poor">{w}</span>'

    if confidence_level < 0.4:
        return '<span class="confidence-low">{w}</span>'

    return '{w}'


def get_speaker_name(config, speaker_id):
    """Get the speaker name from config.extra object given integer speaker_id.
    """
    return config.extra['speakers'][str(speaker_id)]
