# -*- coding: utf-8 -*-
"""
Test if words currently available online parse as expected
"""
import os
from collections import namedtuple

import pytest
import yaml

from duden.search import get


TEST_DATA_DIR = 'tests/test_data'

WordTestRecord = namedtuple('WordTestRecord', ["parsed_word", "expected_dict"])


def generate_word_data():
    """
    Download actual words from duden corresponding to test words from `TEST_DATA_DIR`
    """
    data = []
    for filename in os.listdir(TEST_DATA_DIR):
        full_path = os.path.join(TEST_DATA_DIR, filename)

        # read only yaml files
        if not filename.endswith('.yaml'):
            continue

        # store real and expected result
        with open(full_path, 'r') as f:
            expected_dict = yaml.load(f, Loader=yaml.SafeLoader)
        parsed_word = get(expected_dict['urlname'])

        record = WordTestRecord(parsed_word, expected_dict)
        data.append(record)
    return data


# set up test parameters matrix
word_data = generate_word_data()

basic_attributes = [
    'title', 'name', 'article', 'part_of_speech', 'frequency', 'usage',
    'word_separation', 'synonyms', 'origin', 'words_before', 'words_after'
]

word_param = pytest.mark.parametrize("parsed_word,expected_dict", word_data)
attribute_param = pytest.mark.parametrize("attribute", basic_attributes)


@word_param
@attribute_param
def test_basic_attributes(parsed_word, expected_dict, attribute):
    """Test basic word attributes"""
    assert getattr(parsed_word, attribute) == expected_dict[attribute]


@word_param
def test_meaning_overview(parsed_word, expected_dict):
    """Test meaning overview attribute"""
    assert parsed_word.meaning_overview == expected_dict['meaning_overview']


@word_param
def test_word_compounds(parsed_word, expected_dict):
    """Test word compounds attribute"""
    parsed = parsed_word.compounds
    expected = expected_dict['compounds']

    if parsed == expected == None:  # noqa
        return

    assert parsed.keys() == expected.keys()

    if 'substantive' in expected:
        assert set(parsed['substantive']) == set(expected['substantive'])

    if 'verben' in expected:
        assert set(parsed['verben']) == set(expected['verben'])

    if 'adjektive' in expected:
        assert set(parsed['adjektive']) == set(expected['adjektive'])


@word_param
def test_word_grammar(parsed_word, expected_dict):
    """Test word grammar"""
    expected_grammar = expected_dict['grammar_raw']
    if expected_grammar is not None:
        expected_grammar = [(set(tags), string)
                            for tags, string in expected_grammar]

    assert parsed_word.grammar_raw == expected_grammar

def test_empty_grammar():
    word = get("Wahlbeobachter")
    assert word.grammar_raw == []
    assert word.grammar() == []
