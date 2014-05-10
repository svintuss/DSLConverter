#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: utf-8 -*-
import os, sys

dictionaryFile = open(sys.argv[1], 'r', encoding='utf-8')
dictionaryPath = os.path.dirname(os.path.abspath(sys.argv[1]))
outputFile = open(dictionaryPath + '/' + sys.argv[2], 'w+', encoding='utf-8')

dictionaryContents = dictionaryFile.read().splitlines()

for i in range(len(dictionaryContents)):
    if dictionaryContents[i] == '1':
        outputFile.write('\n')
    elif dictionaryContents[i-1] == '1':
        outputFile.write(dictionaryContents[i] + '\n\t' + dictionaryContents[i] + ' ')
    else:
        outputFile.write(dictionaryContents[i] + ' ')        