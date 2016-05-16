#!/usr/bin/env python
# coding=utf-8

"""
ipapy contains data and functions to work with IPA strings.
"""

from __future__ import absolute_import
from __future__ import print_function
import io
import re
import os

from ipapy.compatibility import hex2unichr
from ipapy.ipachar import IPAConsonant
from ipapy.ipachar import IPAVowel
from ipapy.ipachar import IPADiacritic
from ipapy.ipachar import IPASuprasegmental
from ipapy.ipachar import IPATone

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2016, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "0.0.1"
__email__ = "alberto@albertopettarin.it"
__status__ = "Development"

# constants
DATA_FILE_FIELD_SEPARATOR = u","
DATA_FILE_COMMENT = u"#"
IPA_DATA_FILE_CODEPOINT_SEPARATOR = u" "
IPA_DATA_FILE_COMPOUND_OPERATOR = u"+"
IPA_DATA_FILE_NOT_AVAILABLE = u"N/A"
IPA_DATA_FILE_PATH = u"ipa.dat"

def load_csv_file(relative_file_path, values_per_line=None):
    tuples = []
    file_path = os.path.join(os.path.dirname(__file__), relative_file_path)
    with io.open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if (len(line) > 0) and (not line.startswith(DATA_FILE_COMMENT)):
                # unpack line
                values = line.split(DATA_FILE_FIELD_SEPARATOR)
                if (values_per_line is not None) and (len(values) != values_per_line):
                    raise ValueError("Data file '%s' contains a bad line: '%s'" % (file_path, line))
                tuples.append(tuple(values))
    return tuples

def load_ipa_data():
    ipa_signs = []
    unicode_to_ipa = {}
    ipa_to_unicode = {}
    max_key_length = 0
    for line in load_csv_file(IPA_DATA_FILE_PATH, 3):
        # unpack data
        i_type, i_desc, i_unicode = line

        # create prop string and name string
        prop = "%s %s" % (i_desc, i_type)
        name = re.sub(r" [ ]*", " ", prop)

        # create a suitable IPACharacter obj
        if i_type == "consonant":
            obj = IPAConsonant(name=name, properties=prop)
        elif i_type == "vowel":
            obj = IPAVowel(name=name, properties=prop)
        elif i_type == "diacritic":
            obj = IPADiacritic(name=name, properties=prop)
        elif i_type == "suprasegmental":
            obj = IPASuprasegmental(name=name, properties=prop)
        elif i_type == "tone":
            obj = IPATone(name=name, properties=prop)
        else:
            raise ValueError("The IPA data file contains a bad line, defining an unknown type '%s': '%s'" % (i_type, line))
        ipa_signs.append(obj)

        # map Unicode codepoint to object, if the former is available
        primary_set = False
        for codepoint in i_unicode.split(IPA_DATA_FILE_CODEPOINT_SEPARATOR):
            # deal with compound symbols, like '||' = major-group suprasegmental
            key = None
            if not IPA_DATA_FILE_NOT_AVAILABLE in codepoint:
                key = u"".join([hex2unichr(c) for c in codepoint.split(IPA_DATA_FILE_COMPOUND_OPERATOR)])
            # if we have a key, map it
            if key is not None:
                if key in unicode_to_ipa:
                    raise ValueError("The IPA data file contains a bad line, redefining codepoint '%s': '%s'" % (codepoint, line))
                unicode_to_ipa[key] = obj
                if not primary_set:
                    primary_set = True
                    ipa_to_unicode[obj.canonical_representation] = key
                    obj.unicode_repr = key
                    max_key_length = max(max_key_length, len(key))
    return ipa_signs, unicode_to_ipa, ipa_to_unicode, max_key_length
IPA_SIGNS, UNICODE_TO_IPA, IPA_TO_UNICODE, MAX_KEY_LENGTH_U2I = load_ipa_data()



