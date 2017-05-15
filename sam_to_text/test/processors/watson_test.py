# -*- coding: utf-8 -*-
import unittest

from sam_to_text.transcript_config import TranscriptConfig
from sam_to_text.processors.watson import make_html_from_result


def make_simple_result():
    return {
        'word_confidence': [['Rubery', 0.445]],
        'timestamps': [['Rubery', 0.71, 2.23]],
        'confidence': 0.445,
        'transcript': 'Rubery '
    }


def make_simple_speaker_labels():
    return {
        0.71: {
            'to': 2.23,
            'final': False,
            'confidence': 0.3,
            'speaker': 1,
            'from': 0.71
        }
    }


class MakeHTMLFromResultTest(unittest.TestCase):

    def test_make_html(self):
        result = make_simple_result()
        speaker_labels = make_simple_speaker_labels()
        config = TranscriptConfig(
            'waking-up-test-id',
            'api/watson',
            'Some Podcast',
            ['foo.json'],
            {'speakers': {'1': 'SH'}})
        self.assertEqual(
            make_html_from_result(result, config, speaker_labels),
            ('<p><span class="speaker-name">SH</span> '
             '(<span class="speaker-timestamp">00:00:01</span>): '
             '<span class="confidence-mid">Rubery</span></p>'))



if __name__ == '__main__':
    unittest.main()
