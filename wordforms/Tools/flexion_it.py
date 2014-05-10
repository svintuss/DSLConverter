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


flectionsFile = open('/Users/Alex/Development/Dictionaries development/WordForms/Italian/morph-it/morph-it_048.txt', 'r', encoding='iso-8859-1')

outputflectionsFile = open('/Users/Alex/Development/Dictionaries development/WordForms/wordforms_it.txt', 'w+', encoding='utf-8')

flectionFileContents = flectionsFile.read().splitlines()


for flection in flectionFileContents:
    inputstring = flection.split() 
    
    if inputstring[1] not in words:
        words.append(inputstring[1])
        wordforms.append(inputstring[0])
    else:
        wordforms[words.index(inputstring[1])] = wordforms[words.index(inputstring[1])] + ' ' + inputstring[0]

for i in range(len(words)):
    outputflectionsFile.write(words[i] + '\n')
    outputflectionsFile.write('\t' + wordforms[i] + '\n')