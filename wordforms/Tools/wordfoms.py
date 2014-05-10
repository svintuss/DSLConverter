#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: utf-8 -*-

# Wordforms extractor. This script takes a Hunspell .dic file and extract all wordforms according to rules in .aff file.

import sys
import re 
import os
import shlex

dictionaryFile = open(sys.argv[1], 'r', encoding=sys.argv[2])
outputFile = open(re.sub('.dic', '.txt', sys.argv[1]), 'w', encoding='utf-8')

dictionaryList = dictionaryFile.read().splitlines()


def hunspell(this_word): # this function works with any language if you modify .dic and .aff files
    
    dictionary_entry = this_word
    uniquewordforms = []
    wordforms = os.popen("wordforms -s " + shlex.quote(re.sub('.dic', '.aff', sys.argv[1])) + ' ' + shlex.quote(sys.argv[1]) + ' ' + shlex.quote(this_word)).read().splitlines()
    for i in range(len(wordforms)):
        uniquewordforms.append(wordforms[i])
        
    uniquewordforms.append(dictionary_entry)
    uniquewordforms = list(set(uniquewordforms))   

    return uniquewordforms

for line in dictionaryList:
    if not (line.isdigit() or line.startswith('/')):
        if line.find('/'):
            line = line[:line.find('/')]
        wordforms = hunspell(line)
        outputFile.write(line + '\n\t')
        for word in wordforms:
            outputFile.write(word + ' ')
        outputFile.write('\n')