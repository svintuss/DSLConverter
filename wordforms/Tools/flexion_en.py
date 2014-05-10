#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: utf-8 -*-

# DSL Converter. It should take a Lingvo decompiled .dsl dictionary as input and generate a well-formed XML for OS X Dictionary.app

import sys
import re               #import regular expressions module
import urllib.parse     # urllib.parse.quote_plus('string_of_characters_like_these:$#@=?%^Q^$')
                        # 'string_of_characters_like_these%3A%24%23%40%3D%3F%25%5EQ%5E%24'
import os
import pipes 
import shlex
import unicodedata

wordforms = []
words = []


flectionsFile = open('/Users/Alex/Development/Dictionaries development/WordForms/English/agid-4/infl.txt', 'r', encoding='utf-8')

outputflectionsFile = open('/Users/Alex/Development/Dictionaries development/WordForms/wordforms_en.txt', 'w+', encoding='utf-8')

flectionFileContents = flectionsFile.read().splitlines()

for flection in flectionFileContents:
    mainword = flection[:flection.index(':')]
    word = mainword.split()
    indexword = word[0]
    
    flexed_word = flection[flection.index(':')+1:]
    flexed_word = re.sub('[?~,<>]', '', flexed_word)
    flexed_word = re.sub('[1234567890]' + ' ', '', flexed_word)
    flexed_word = re.sub('[. ]' + '[1234567890]', '', flexed_word)
    flexed_word = re.sub('\| ', '', flexed_word)
    words.append(indexword)
    wordforms.append(flexed_word)
 
for i in range(len(words)):
    outputflectionsFile.write(words[i] + '\n')
    outputflectionsFile.write('\t' + words[i] + ' ' + wordforms[i] + '\n')