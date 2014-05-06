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
import tidylib
from tidylib import tidy_document
import time
import math



tidylib.BASE_OPTIONS = {
    "output-xml" : 0,
    "input-xml" : 0,
    "show-warnings" : 0,
    "quote-marks" : 0,
    "quote-nbsp" : 0,
    "quote-ampersand" : 0,
    "break-before-br" : 0,
    "uppercase-tags" : 0,
    "uppercase-attributes" : 0,
    "char-encoding" : "utf8",
    "new-pre-tags" : "div, font",
    "new-blocklevel-tags" : "d:entry, d:index, d:dictionary, embed",
    "drop-proprietary-attributes" : 0,
    "wrap" : 0,
    "merge-divs" : 1,
    "indent" : 0,
    "clean" : 0,
    "tidy-mark" : 0,
    "show-body-only" : 1,
    "output-encoding" : "utf8",
    "quiet" : 1,
    "newline" : "LF",
    "doctype" : "omit",
    "add-xml-space" : 0,
    "write-back" : 0    
    }


# Some global variables declaration. Theese are needed to process index values correctly.
entryText = ''
myTag = ''
entryContents = ''
titleString = ''
gIndexStrings = ''
gEntryTitle = ''
gM = '' 
gEX = ''
gEntriesList = []
wordforms = []
words = []
gIndexEnable = 1
gPhrases ='\n'

english_noIndexList = [
    'to',
    'the',
    'a',
    'an',
    'I',
    'me',
    'you',
    'he',
    'we',
    'they',
    'in',
    'at'
    ]
    
french_noIndexList = [
    'de',
    'du',
    'a',
    'au',
    'aux',
    'qui',
    'que',
    'y',
    'en',
    'des',
    'ce',
    'à',
        
    ]

italian_noIndexList = [
    'un',
    'uno',
    'una',
    "un",
    'il',
    'lo',
    'i',
    'gli',
    'le',
    'del',
    'al',
    'dal',
    'nel',
    'sul',
    'dello', 'allo', 'dallo', 'nello', 'sullo', 'della', 'alla', 'dalla', 'nella', 'sulla',
    "dell'", "all'", "dall'", "nell'", "sull'",
    "dei", "ai", "dai", "nei", "sui",
    "degli", "agli", "dagli", "negli", "sugli",
    "delle", "alle", "dalle", "nelle", "sulle"
    ]


# Open and create dictionary files
dictionaryFile = open(sys.argv[1], 'r', encoding='utf-16le')
XMLfile = open(re.sub('.dsl', '.xml', sys.argv[1]), 'w+', encoding='utf-8') # this is the output file
try:
    abbreviationsFile = open(re.sub('.dsl', '_abrv.dsl', sys.argv[1]), 'r', encoding='utf-16le')
    abbreviationsContents = abbreviationsFile.read().replace(u'\ufeff', '')  #.encode('utf-8')
    gAbbreviationsList = abbreviationsContents.splitlines()
except FileNotFoundError:
    gAbbreviationsList = ''
    
try:
    annotationFile = open(re.sub('.dsl', '.ann', sys.argv[1]), 'r', encoding='utf-16le')
    annotationContents = annotationFile.read().replace(u'\ufeff', '')  #.encode('utf-8')
    annotationList = annotationContents.splitlines()
except FileNotFoundError:
    annotationList = ''
    
flectionsFile = open('/Users/Alex/Development/Dictionaries development/WordForms/' + 'wordforms_' + sys.argv[2] + '.txt', 'r', encoding='utf-8')

dictionaryContents = dictionaryFile.read().replace(u'\ufeff', '') #.encode('utf-8')
dictionaryList = dictionaryContents.splitlines() # convert dictionary from UTF-16 to UTF-8 and to an array  of lines

    
flectionFileContents = flectionsFile.read().splitlines()

if sys.argv[2] == 'en':
    gNoIndexList = english_noIndexList
elif sys.argv[2] == 'fr':
    gNoIndexList = french_noIndexList
elif sys.argv[2] == 'it':
    gNoIndexList = italian_noIndexList
else:
    gNoIndexList = []

XMLfile.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<d:dictionary xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:d=\"http://www.apple.com/DTDs/DictionaryService-1.0.rng\">\n\n')

XMLfile.write('<d:entry id="front_back_matter" d:title="Front/Back Matter">')

for annotationLine in annotationList:
    if annotationLine != '' and not annotationLine.startswith('#'):
        
        if annotationLine.startswith('\t'):
            XMLfile.write('<div class="description">' + annotationLine[1:] + '</div><br />\n')
        else:
            XMLfile.write('<div class="label">' + annotationLine + '</div>\n')

XMLfile.write('	</d:entry>\n')       

def update_progress(progress):
    barLength = 60 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rConverting: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), int(round(progress*100)), status)
    sys.stdout.write(text)
    sys.stdout.flush()
        
def processDSLTag(myTag, myString):
    global gIndexStrings
    global gEntryTitle
    global gM
    global gEX
    global EntryNameForms
    global gIndexEnable
    
    DSLTags = ("[b]", "[/b]", 
                "[i]", "[/i]", 
                "[u]", "[/u]", 
                "[c]",
                '[c aliceblue]',
                '[c antiquewhite]',
                '[c aqua]',
                '[c aquamarine]',
                '[c azure]',
                '[c beige]',
                '[c bisque]',
                '[c black]',
                '[c blanchedalmond]',
                '[c blue]',
                '[c blueviolet]',
                '[c brown]',
                '[c burlywood]',
                '[c cadetblue]',
                '[c chartreuse]',
                '[c chocolate]',
                '[c coral]',
                '[c cornflowerblue]',
                '[c cornsilk]',
                '[c crimson]',
                '[c cyan]',
                '[c darkblue]',
                '[c darkcyan]',
                '[c darkgoldenrod]',
                '[c darkgray]',
                '[c darkgreen]',
                '[c darkkhaki]',
                '[c darkmagenta]',
                '[c darkolivegreen]',
                '[c darkorange]',
                '[c darkorchid]',
                '[c darkred]',
                '[c darksalmon]',
                '[c darkseagreen]',
                '[c darkslateblue]',
                '[c darkslategray]',
                '[c darkturquoise]',
                '[c darkviolet]',
                '[c deeppink]',
                '[c deepskyblue]',
                '[c dimgray]',
                '[c dodgerblue]',
                '[c firebrick]',
                '[c floralwhite]',
                '[c forestgreen]',
                '[c fuchsia]',
                '[c gainsboro]',
                '[c ghostwhite]',
                '[c gold]',
                '[c goldenrod]',
                '[c gray]',
                '[c green]',
                '[c greenyellow]',
                '[c honeydew]',
                '[c hotpink]',
                '[c indianred]',
                '[c indigo]',
                '[c ivory]',
                '[c khaki]',
                '[c lavender]',
                '[c lavenderblush]',
                '[c lawngreen]',
                '[c lemonchiffon]',
                '[c lightblue]',
                '[c lightcoral]',
                '[c lightcyan]',
                '[c lightgoldenrodyellow]',
                '[c lightgray]',
                '[c lightgreen]',
                '[c lightpink]',
                '[c lightsalmon]',
                '[c lightseagreen]',
                '[c lightskyblue]',
                '[c lightslategray]',
                '[c lightsteelblue]',
                '[c lightyellow]',
                '[c lime]',
                '[c limegreen]',
                '[c linen]',
                '[c magenta]',
                '[c maroon]',
                '[c mediumaquamarine]',
                '[c mediumblue]',
                '[c mediumorchid]',
                '[c mediumpurple]',
                '[c mediumseagreen]',
                '[c mediumslateblue]',
                '[c mediumspringgreen]',
                '[c mediumturquoise]',
                '[c mediumvioletred]',
                '[c midnightblue]',
                '[c mintcream]',
                '[c mistyrose]',
                '[c moccasin]',
                '[c navajowhite]',
                '[c navy]',
                '[c oldlace]',
                '[c olive]',
                '[c olivedrab]',
                '[c orange]',
                '[c orangered]',
                '[c orchid]',
                '[c palegoldenrod]',
                '[c palegreen]',
                '[c paleturquoise]',
                '[c palevioletred]',
                '[c papayawhip]',
                '[c peachpuff]',
                '[c peru]',
                '[c pink]',
                '[c plum]',
                '[c powderblue]',
                '[c purple]',
                '[c red]',
                '[c rosybrown]',
                '[c royalblue]',
                '[c saddlebrown]',
                '[c salmon]',
                '[c sandybrown]',
                '[c seagreen]',
                '[c seashell]',
                '[c sienna]',
                '[c silver]',
                '[c skyblue]',
                '[c slateblue]',
                '[c slategray]',
                '[c snow]',
                '[c springgreen]',
                '[c steelblue]',
                '[c tan]',
                '[c teal]',
                '[c thistle]',
                '[c tomato]',
                '[c turquoise]',
                '[c violet]',
                '[c wheat]',
                '[c white]',
                '[c whitesmoke]',
                '[c yellow]',
                '[c yellowgreen]',
                "[/c]", 
                "[*]", "[/*]", 
                "[m1]", "[m2]", 
                "[m3]", "[m4]", 
                "[m5]", "[m6]", 
                "[m7]", "[m8]", 
                "[m9]", "[/m]", 
                "[trn]", "[/trn]", 
                "[ex]", "[/ex]", 
                "[com]", "[/com]", 
                "[!trs]", "[/!trs]", 
                "[s]", 
                "[s_img]",
                "[/s]", 
                "[url]", "[/url]", 
                "[p]", "[/p]", 
                "[']", "[/']", 
                "[lang]", "[/lang]", 
                "[ref]", "[/ref]", 
                "[t]", "[/t]",
                "[sup]", "[/sup]",
                "[sub]", "[/sub]")
                
    XMLTags = ("<b>", "</b>", 
                "<i>", "</i>", 
                "<u>", "</u>", 
                "<font color=\"#007F00\">", 
                "<font color=\"#F0F8FF\">",
                "<font color=\"#FAEBD7\">",
                "<font color=\"#00FFFF\">",
                "<font color=\"#7FFFD4\">",
                "<font color=\"#F0FFFF\">",
                "<font color=\"#F5F5DC\">",
                "<font color=\"#FFE4C4\">",
                "<font color=\"#000000\">",
                "<font color=\"#FFEBCD\">",
                "<font color=\"#0000FF\">",
                "<font color=\"#8A2BE2\">",
                "<font color=\"#A52A2A\">",
                "<font color=\"#DEB887\">",
                "<font color=\"#5F9EA0\">",
                "<font color=\"#7FFF00\">",
                "<font color=\"#D2691E\">",
                "<font color=\"#FF7F50\">",
                "<font color=\"#6495ED\">",
                "<font color=\"#FFF8DC\">",
                "<font color=\"#DC143C\">",
                "<font color=\"#00FFFF\">",
                "<font color=\"#00008B\">",
                "<font color=\"#008B8B\">",
                "<font color=\"#B8860B\">",
                "<font color=\"#A9A9A9\">",
                "<font color=\"#006400\">",
                "<font color=\"#BDB76B\">",
                "<font color=\"#8B008B\">",
                "<font color=\"#556B2F\">",
                "<font color=\"#FF8C00\">",
                "<font color=\"#9932CC\">",
                "<font color=\"#8B0000\">",
                "<font color=\"#E9967A\">",
                "<font color=\"#8FBC8F\">",
                "<font color=\"#483D8B\">",
                "<font color=\"#2F4F4F\">",
                "<font color=\"#00CED1\">",
                "<font color=\"#9400D3\">",
                "<font color=\"#FF1493\">",
                "<font color=\"#00BFFF\">",
                "<font color=\"#696969\">",
                "<font color=\"#1E90FF\">",
                "<font color=\"#B22222\">",
                "<font color=\"#FFFAF0\">",
                "<font color=\"#228B22\">",
                "<font color=\"#FF00FF\">",
                "<font color=\"#DCDCDC\">",
                "<font color=\"#F8F8FF\">",
                "<font color=\"#FFD700\">",
                "<font color=\"#DAA520\">",
                "<font color=\"#808080\">",
                "<font color=\"#008000\">",
                "<font color=\"#ADFF2F\">",
                "<font color=\"#F0FFF0\">",
                "<font color=\"#FF69B4\">",
                "<font color=\"#CD5C5C\">",
                "<font color=\"#4B0082\">",
                "<font color=\"#FFFFF0\">",
                "<font color=\"#F0E68C\">",
                "<font color=\"#E6E6FA\">",
                "<font color=\"#FFF0F5\">",
                "<font color=\"#7CFC00\">",
                "<font color=\"#FFFACD\">",
                "<font color=\"#ADD8E6\">",
                "<font color=\"#F08080\">",
                "<font color=\"#E0FFFF\">",
                "<font color=\"#FAFAD2\">",
                "<font color=\"#D3D3D3\">",
                "<font color=\"#90EE90\">",
                "<font color=\"#FFB6C1\">",
                "<font color=\"#FFA07A\">",
                "<font color=\"#20B2AA\">",
                "<font color=\"#87CEFA\">",
                "<font color=\"#778899\">",
                "<font color=\"#B0C4DE\">",
                "<font color=\"#FFFFE0\">",
                "<font color=\"#00FF00\">",
                "<font color=\"#32CD32\">",
                "<font color=\"#FAF0E6\">",
                "<font color=\"#FF00FF\">",
                "<font color=\"#800000\">",
                "<font color=\"#66CDAA\">",
                "<font color=\"#0000CD\">",
                "<font color=\"#BA55D3\">",
                "<font color=\"#9370DB\">",
                "<font color=\"#3CB371\">",
                "<font color=\"#7B68EE\">",
                "<font color=\"#00FA9A\">",
                "<font color=\"#48D1CC\">",
                "<font color=\"#C71585\">",
                "<font color=\"#191970\">",
                "<font color=\"#F5FFFA\">",
                "<font color=\"#FFE4E1\">",
                "<font color=\"#FFE4B5\">",
                "<font color=\"#FFDEAD\">",
                "<font color=\"#000080\">",
                "<font color=\"#FDF5E6\">",
                "<font color=\"#808000\">",
                "<font color=\"#6B8E23\">",
                "<font color=\"#FFA500\">",
                "<font color=\"#FF4500\">",
                "<font color=\"#DA70D6\">",
                "<font color=\"#EEE8AA\">",
                "<font color=\"#98FB98\">",
                "<font color=\"#AFEEEE\">",
                "<font color=\"#DB7093\">",
                "<font color=\"#FFEFD5\">",
                "<font color=\"#FFDAB9\">",
                "<font color=\"#CD853F\">",
                "<font color=\"#FFC0CB\">",
                "<font color=\"#DDA0DD\">",
                "<font color=\"#B0E0E6\">",
                "<font color=\"#800080\">",
                "<font color=\"#FF0000\">",
                "<font color=\"#BC8F8F\">",
                "<font color=\"#4169E1\">",
                "<font color=\"#8B4513\">",
                "<font color=\"#FA8072\">",
                "<font color=\"#F4A460\">",
                "<font color=\"#2E8B57\">",
                "<font color=\"#FFF5EE\">",
                "<font color=\"#A0522D\">",
                "<font color=\"#C0C0C0\">",
                "<font color=\"#87CEEB\">",
                "<font color=\"#6A5ACD\">",
                "<font color=\"#708090\">",
                "<font color=\"#FFFAFA\">",
                "<font color=\"#00FF7F\">",
                "<font color=\"#4682B4\">",
                "<font color=\"#D2B48C\">",
                "<font color=\"#008080\">",
                "<font color=\"#D8BFD8\">",
                "<font color=\"#FF6347\">",
                "<font color=\"#40E0D0\">",
                "<font color=\"#EE82EE\">",
                "<font color=\"#F5DEB3\">",
                "<font color=\"#FFFFFF\">",
                "<font color=\"#F5F5F5\">",
                "<font color=\"#FFFF00\">",
                "<font color=\"#9ACD32\">",
                "</font>", 
                "<span d:priority=\"2\">", "</span>", 
                "<div class=\"L1\">", "<div class=\"L2\">", 
                "<div class=\"L3\">", "<div class=\"L4\">", 
                "<div class=\"L5\">", "<div class=\"L6\">", 
                "<div class=\"L7\">", "<div class=\"L8\">", 
                "<div class=\"L9\">", "</div>", 
                "", "", 
                "<font color=\"#7F7F7F\" id=\"", "</font>", 
                "", "", 
                "", "", 
                "&#160;<embed  height=\"16\" width=\"16\" autoplay=\"false\" src=\"media/", 
                "<img src=\"media/",
                "\" />", 
                "<a href=\"", "</a>", 
                "<font class=\"mark\" title=\"", "</font>", 
                "<em class=\"accent\">", "</em>", 
                "", "", 
                "<a STYLE=\"text-decoration: none\" href=\"x-dictionary:r:", "</a>", 
                "<span class=\"transcription\">", "</span>",  
                "<sup>", "</sup>",
                "<sub>", "</sub>")
    
    if myTag == '[!trs]':
        gIndexEnable = 0
    if myTag == '[/!trs]':
        gIndexEnable = 1

    if myTag[:5] == '[lang':
        myTag = '[lang]'
    
    if myTag == "[s]" and myString.find('.wav') == -1: #or myString.find('.avi') == -1):
        myTag = "[s_img]"
    
    
    i = DSLTags.index(myTag) if myTag in DSLTags else -1 
    
    if i != -1:
        outputTag = XMLTags[i]
        
        if '[m' in myTag:
            gM = myTag
        
        if myTag == '[ex]':

            gEX = myTag

            if gIndexEnable: #index contents only outside [!trs] tag
            
                if myString.find("[/lang]") != -1:
                    tagContents = myString[:myString.find('[/lang]')]
                else:
                    tagContents = myString
                
#                if tagContents.find("[p]") != -1: # i think I made this string for some buggy French dictionary
#                    tagContents = tagContents[:tagContents.find('[p]')]
            
                tagTitle = remove_DSLmarkup(tagContents, 'true')
                tagTitle = re.sub('"', '', tagTitle)
                reducedtagTitle = tagTitle.split()
            
                tagTitle = ' '.join(reducedtagTitle[:10])
            
                if tagTitle in EntryNameForms:
                    tagTitle = tagTitle + '_1'

                encodedTagID = urllib.parse.quote_plus(tagTitle) #encode_text(tagTitle, true, false)

                outputTag = outputTag + encodedTagID + '">'
                gIndexStrings = gIndexStrings + '	<d:index d:value="' + tagTitle  + '" d:title="' + tagTitle + '"  d:anchor="xpointer(//*[@id=\'' + encodedTagID + '\'])"/>' + "\n"        
        elif myTag == "[/ex]":
            gEX = ''
        
        elif myTag == "[ref]":
            tagContents = myString[:myString.find('[/ref]')]
            tagContents = tagContents.replace(' ', '_')
            outputTag = outputTag + '_' + urllib.parse.quote_plus(remove_DSLmarkup(tagContents, 'true')) + '">'
        
        elif myTag == "[url]":
            tagContents = myString[:myString.find('[/url]')]
            outputTag = outputTag + tagContents + '">'
        
        elif myTag == "[p]":
            abbreviation = myString[:myString.find('[/p]')]
            abbreviation = remove_DSLmarkup(abbreviation, 'false')
            abbreviation = processAbbreviations(abbreviation)
            outputTag = outputTag + abbreviation + '">'
        
        return outputTag
            
    else:
        return myTag

def processDSLstring(thisString):
    global gM
    global gEX
    
    if gM != '':
        thisString = gM + thisString
        if not thisString.endswith('[/m]'):
            thisString = thisString + '[/m]'
    
    if gEX != '':
        thisString = thisString.replace("[lang", "[ex][lang")
    
    outside_tag = 'true'
    clean_text = ''
    previous_char = ''
    this_char = ''
    myString = ''
    
    for i in range(len(thisString)):
        this_char = thisString[i]
        if this_char == '[':
            if previous_char == '\\':
#                outside_tag = 'true'
                clean_text = clean_text + this_char
            else:
                outside_tag = 'false'
                this_tag = this_char
        elif this_char == ']':
            if previous_char == '\\':
 #               outside_tag = 'true'
                clean_text = clean_text + this_char
            else:
                outside_tag = 'true'
                this_tag = this_tag + this_char

                myString = thisString[i:]
                clean_text = clean_text + processDSLTag(this_tag, myString)
                
        elif this_char == '\\':
            outside_tag = 'true'
        elif outside_tag == 'true':
            clean_text = clean_text + this_char
        elif outside_tag == 'false':
            this_tag = this_tag + this_char
        previous_char = this_char
    
    return clean_text
                
    

def remove_DSLmarkup(this_text, p):
    copy_flag = 'true'
    clean_text = ''
    previous_char = ''
    this_tag = ''
    
    for this_char in this_text:
            
        if this_char =='[':
            if previous_char == '\\':
                clean_text = clean_text + this_char
            else:
                copy_flag = 'false'
                this_tag = this_char
        elif this_char == ']':
            if previous_char =='\\':
                clean_text = clean_text + this_char
            else:
                copy_flag = 'true'
                this_tag = this_tag + this_char
        elif this_char =='\\':
            copy_flag = 'true'
        elif (p == 'true' and this_tag == '[p]'):
            copy_flag == 'false'
        elif copy_flag == 'true':
            clean_text = clean_text + this_char
        elif (p == 'true' and this_tag == '[/p]'):
            copy_flag == 'true'
        else:
            this_tag = this_tag + this_char
         
        previous_char = this_char
    
    return clean_text
	

def processAbbreviations(abbreviation): # finish 
    global gAbbreviationsList
    try:
        i = gAbbreviationsList.index(abbreviation) + 1 # list_position(abbreviation, gAbbreviationsList) + 1
    except ValueError:
        return ''
    definition = gAbbreviationsList[i]
    definition = definition[1:]
    return definition



def spell(this_word): #modify this function so that it handles "-" and "'" well
    global gNoIndexList
    global words
    global wordforms
    
    uniquewordforms = ''
    originalword = this_word
    this_word = re.sub('[!?.,¿:;()]', '', this_word)
    
    if (this_word.startswith("-") or this_word.startswith("'")):
        uniquewordforms = uniquewordforms + ' ' + this_word[1:]
        returnwordforms = uniquewordforms.split()
        returnwordforms.append(originalword) 
        returnwordforms = list(set(returnwordforms))
        return returnwordforms
        
    if this_word.startswith("s'") or this_word.startswith("l'"):
        this_word = this_word[2:]
    
    if this_word.startswith('se '):
        this_word = this_word[3:]
        
    this_word = this_word.split() # convert string to the list of words

    for word in this_word:
        if word not in gNoIndexList:
            if word in words:
                uniquewordforms = uniquewordforms + ' ' + wordforms[words.index(word)]
    
    returnwordforms = uniquewordforms.split()
    returnwordforms.append(originalword)  
    returnwordforms = list(set(returnwordforms))     

    return returnwordforms
    
def clean_Title(this_text):
    copy_flag = 'true'
    clean_text = ''
    
    for this_char in this_text:
        if this_char == '{':
            copy_flag = 'false'
        elif this_char == '}':
            copy_flag = 'true'
        elif copy_flag == 'true':
            clean_text = clean_text + this_char
    
    return clean_text
 
def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])        
    

# process worforms from wordforms file

for flection in flectionFileContents:
    
    if flection.startswith('\t'):
        wordforms.append(flection[1:])
    else:
        words.append(flection)
    
# Main converter function


stringCount = len(dictionaryList)

for i in range(stringCount):
    update_progress(i/stringCount)
    thisString = dictionaryList[i]
    try:
        nextString = dictionaryList[i+1]
    except IndexError:
        nextString = '' 
        
               
    thisString = re.sub('<', '〈', thisString)
    thisString = re.sub('>', '〉', thisString)
    thisString = thisString.replace('\\(', '(')
    thisString = thisString.replace('\\)', ')')
    tempString = ''
        
    if (thisString[:1] != '#' and thisString != ''):
        if thisString[:1] != '	':
            if gEntryTitle != '': # tidy and write previous entry to file
                
                XMLfile.write(titleString + gIndexStrings + '		<div class=\"title\">' + processDSLstring(gEntryHeader) + '</div>' + entryContents + '</d:entry>\n')
                
            entryContents = ''
            gEntryHeader = re.sub('[{}]', '', thisString)
            gEntryTitle = clean_Title(thisString)
            gEntryTitle = re.sub('^\.\.\.', '', gEntryTitle)
            if gEntryTitle in gEntriesList:
                EntryTitle = gEntryTitle + '_1'
            else:
                EntryTitle = gEntryTitle
                gEntriesList.append(gEntryTitle)
            
            titleString = '\n<d:entry id=\"' + '_' + urllib.parse.quote_plus(re.sub(' ', '_', EntryTitle)) + '\" d:title=\"' + gEntryTitle + '\">' + '\n'
            EntryNameForms = spell(gEntryTitle)
            if EntryNameForms != '':
                gIndexStrings = ''
                for i in EntryNameForms:
                    gIndexStrings = gIndexStrings + '	<d:index d:value=\"' + i + '\" d:title=\"' +gEntryTitle + '\"/>\n'
            else:
                gIndexStrings = '	<d:index d:value=\"' + gEntryTitle + '\" d:title=\"' + gEntryTitle + '\"/>' + '\n'
            

        elif thisString.startswith('	'):
            
            thisString = thisString[1:]
            
            if nextString.startswith('	'):
                nextString = nextString[1:]
            if (nextString.startswith('[m') or nextString == '' ) and not thisString.endswith('[/m]') and thisString.startswith('[m'):
                thisString = thisString + '[/m]'

            tempString = processDSLstring(thisString)
                
                        
            if (gM == '' and not thisString.endswith("[/m]")): # if this is a main line without opening and closing m tags add Div Class 0
                tempString = "		<div class=\"L0\">" + tempString + "</div>\n"

            if thisString.endswith("[/m]"):
                gM = ''
                
           
            tempString, errors = tidy_document(tempString)                       
            
            tempString = re.sub('> <', '>&#160;<', tempString) 
            tempString = re.sub('.wav">', '.mp3" />', tempString) # replace links to .wav files and make proper closing tags TRY TO REWRITE THIS THROUGH MODIFYING TIDY PROPERTIES
#            tempString = re.sub('\n', '', tempString)            
            tempString = re.sub('.jpg">', '.jpg" />', tempString) 
            tempString = re.sub('.JPG">', '.JPG" />', tempString) 
            tempString = re.sub('.tif">', '.tif" />', tempString) 
            tempString = re.sub('.TIF">', '.TIF" />', tempString)
            tempString = re.sub('.bmp">', '.bmp" />', tempString)                          
            tempString = re.sub('.BMP">', '.BMP" />', tempString) 

            entryContents = entryContents + tempString
    
    entryContents = re.sub("\\]", "]", entryContents)
    entryContents = re.sub("\\[", "[", entryContents)

if entryContents == '':
    XMLfile.write('\n</d:dictionary>')
else:
    XMLfile.write(titleString + gIndexStrings + "		<div class=\"title\">" + gEntryTitle + "</div>" + entryContents + "\n</d:entry>\n" + "\n</d:dictionary>")

