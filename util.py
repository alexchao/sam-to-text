# -*- coding: utf-8 -*-
import re


RE_FILE_SLUG = re.compile(
    '(?P<doc_id>waking-up-\d\d\d-(?P<title_slug>[a-z-]+)).json')


def get_id_and_title_from_file_path(file_path):
    match = re.search(RE_FILE_SLUG, file_path)
    if not match:
        raise Exception('Didn\'t find title slug in "{}"'.format(file_path))
    matches = match.groupdict()
    return matches['doc_id'], matches['title_slug'].replace('-', ' ').capitalize()
