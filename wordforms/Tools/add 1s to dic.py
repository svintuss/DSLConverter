#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: utf-8 -*-


#import hunspell, sys

# hobj = hunspell.HunSpell('/Users/Alex/uk-UA.dic', '/Users/Alex/uk-UA.aff')
# print(hobj.suggest('был'))

dictionaryFile = open('/Users/Alex/cs.dic', 'r', encoding='ISO8859-2')
outputFile = open('/Users/Alex/cs_2.dic', 'w+', encoding='ISO8859-2')

dictionaryContents = dictionaryFile.read().splitlines()

for line in dictionaryContents:
    outputFile.write(line + '\n1\n')
