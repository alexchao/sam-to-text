# -*- coding: utf-8 -*-
import unittest

from transcript_config import ConfigType
from transcript_config import read_config


TEST_CONFIG_PATH = 'test-data/test-config.json'


class ReadConfigTest(unittest.TestCase):

    def test_read(self):
        configs = read_config(TEST_CONFIG_PATH)
        self.assertEqual(configs[0].id, 'waking-up-005-charlie-hebdo')
        self.assertEqual(configs[0].type, ConfigType.GCS)
        self.assertEqual(configs[0].title, 'After Charlie Hebdo and Other Thoughts')
        self.assertEqual(
            configs[0].source_files,
            [
                'test-data/waking-up-005-charlie-hebdo-1.json',
                'test-data/waking-up-005-charlie-hebdo-2.json'
            ]
        )

        self.assertEqual(configs[1].id, 'waking-up-008-ama01')
        self.assertEqual(configs[1].type, ConfigType.WATSON)
        self.assertEqual(configs[1].title, 'Ask Me Anything #1')
        self.assertEqual(
            configs[1].source_files,
            ['test-data/waking-up-008-ama01.json']
        )


if __name__ == '__main__':
    unittest.main()
