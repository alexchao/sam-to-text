# -*- coding: utf-8 -*-
import unittest

from sam_to_text.processors.transcript_chunker import TranscriptChunker


class TranscriptChunkerTest(unittest.TestCase):

    def test_single_chunk(self):
        chunker = TranscriptChunker(max_length=10)
        chunker.add_transcript('alex', '<p>alex</p>')
        chunks = chunker.get_chunks()
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].raw, 'alex')
        self.assertEqual(chunks[0].html, '<p>alex</p>')

    def test_multiple_chunk(self):
        chunker = TranscriptChunker(max_length=10)
        chunker.add_transcript('abc', '<p>abc</p>')
        chunker.add_transcript('def', '<p>def</p>')
        chunker.add_transcript('ghi', '<p>ghi</p>')
        chunker.add_transcript('jkl', '<p>jkl</p>')
        chunker.add_transcript('mno', '<p>mno</p>')
        chunker.add_transcript('pqr', '<p>pqr</p>')
        chunker.add_transcript('stu', '<p>stu</p>')
        chunker.add_transcript('vwx', '<p>vwx</p>')
        chunker.add_transcript('yza', '<p>yza</p>')
        chunks = chunker.get_chunks()
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0].raw, 'abc def ghi jkl')
        self.assertEqual(
            chunks[0].html,
            '<p>abc</p><p>def</p><p>ghi</p><p>jkl</p>')
        self.assertEqual(chunks[1].raw, 'mno pqr stu vwx')
        self.assertEqual(
            chunks[1].html,
            '<p>mno</p><p>pqr</p><p>stu</p><p>vwx</p>')
        self.assertEqual(chunks[2].raw, 'yza')
        self.assertEqual(chunks[2].html, '<p>yza</p>')


if __name__ == '__main__':
    unittest.main()
