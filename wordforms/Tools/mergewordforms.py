#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: utf-8 -*-

# Wordforms extractor. This script takes a Hunspell .dic file and extract all wordforms according to rules in .aff file.

import sys
import re 
import os
import shlex


flectionsFile = open(sys.argv[1], 'r', encoding='utf-8')
flectionFileContents = flectionsFile.read().splitlines()
verbsFile = open(sys.argv[2], 'r', encoding='utf-8')
verbsFileContents = verbsFile.read().splitlines()
outputFile = open(re.sub('.txt', '1.txt', sys.argv[1]), 'w', encoding='utf-8')
wordforms = []
words = []
verbforms = []
verb = []

for flection in flectionFileContents:
    if flection.startswith('\t'):
        wordforms.append(flection[1:])
    else:
        words.append(flection)
        
for line in verbsFileContents:
    verb = line[:line.find(':')]
    verbforms = re.sub(';',' ', line[line.find(':')+2:])
    try:
        wordforms[words.index(verb)] = wordforms[words.index(verb)] + ' ' + verbforms
    except ValueError:
        words.append(verb)
        wordforms.append(verbforms)

for i in range(len(words)):
    outputFile.write(words[i] + '\n')
    outputFile.write('\t' + wordforms[i] + '\n')