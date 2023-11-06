#!/usr/bin/env python3
#
#    isame_xml2txt.py
#
# convert xml output of Archetype from the InterSaME project and convert to InterSaME text transcription format.
#
# nested tags of the same type are *not* supported, i.e..:
#     <a> foo <a> bar </a> xx </a>
#
# the order of adding several annotation tags to the same text in Archetype is meaningful:
#   => unclear > fasila > variant [{*1DS02}/ø=sub=sub.fasila]
#
# Dependencies
# ------------
#   * local_settings.py: archetype configuration file for text editor menus
#
# TODO
# ----
#   * lacuna, unclear or illegible cannot cover an index mark. The only exception if a lacuna covering only an index mark,
#     i.e., without any right or left context
#   * regex q cambie {...#} por {...}#
#
# example:
#   $ python isame_xml2txt.py -f ../../data/arabic/trans/F003_BnF.Ar.330b-trans.xml > ../../data/arabic/trans/F003_BnF.Ar.330b.txt
#
# example with whole processing of F003:
#   $ python isame_xml2txt.py -f ../../data/arabic/trans/F003_BnF.Ar.330b-3-trans.xml|
#     tee ../../data/arabic/trans/F003_BnF.Ar.330b-4.txt | python isame_parser.py |
#     tee ../../data/arabic/trans/F003_BnF.Ar.330b-5-pre.json | python isame_mapper.py |
#     tee ../../data/arabic/trans/F003_BnF.Ar.330b-6.json | python isame_json2tei.py > ../../data/arabic/trans/F003_BnF.Ar.330b-7.xml
#
# example with F001:
#   $ python isame_xml2txt.py -f ../../data/arabic/trans/F001_BnF.Ar.330f-3-trans.xml |
#     sed 's/#1#/#/g' | sed 's/|-|φ#SWRH#ALMABDH#MABH#WESRWN#WBLB#ABB#//g' |
#     tee ../../data/arabic/trans/F001_BnF.Ar.330f-4.txt | python isame_parser.py |
#     tee ../../data/arabic/trans/F001_BnF.Ar.330f-5-pre.json | python isame_mapper.py |
#     tee ../../data/arabic/trans/F001_BnF.Ar.330f-6.json | python isame_json2tei.py | tee ../../data/arabic/trans/F001_BnF.Ar.330f-7.xml
#
#   $ python isame_xml2txt.py -f ../../data/arabic/trans/F001_OIC.A6961-3-trans.xml |
#     tee ../../data/arabic/trans/F001_OIC.A6961-4.txt | python isame_parser.py |
#     tee ../../data/arabic/trans/F001_OIC.A6961-5-pre.json | python isame_mapper.py |
#     tee ../../data/arabic/trans/F001_OIC.A6961-6.json | python isame_json2tei.py | tee ../../data/arabic/trans/F001_OIC.A6961-7.xml
#
# complete F001:
#   $ python isame_xml2txt.py -f ../../data/arabic/trans/F001_BnF.Ar.330f-3-trans.xml ../../data/arabic/trans/F001_OIC.A6961-3-trans.xml |
#     sed 's/#1#/#/g' | sed 's/|-|φ#SWRH#ALMABDH#MABH#WESRWN#WBLB#ABB#//g' |
#     tee ../../data/arabic/trans/F001-4.txt | python isame_parser.py |
#     tee ../../data/arabic/trans/F001-5-pre.json | python isame_mapper.py |
#     tee ../../data/arabic/trans/F001-6.json | python isame_json2tei.py | tee ../../data/arabic/trans/F001-7.xml
#
# D001:
#   $ python isame_xml2txt.py -f ../../data/arabic/trans/D001_UbT.Ma.VI.165-3-trans.xml | tee ../../data/arabic/trans/D001_UbT.Ma.VI.165-4.txt |
#     python isame_parser.py | tee D001_UbT.Ma.VI.165-5-pre.json | python isame_mapper.py | tee D001_UbT.Ma.VI.165-6.json
#
# F005
#   $ python isame_xml2txt.py -f ../../data/arabic/trans/F005_BnF.Ar.329c-3-trans.xml | tee ../../data/arabic/trans/F005_BnF.Ar.329c-4.txt |
#     python isame_parser.py | tee ../../data/arabic/trans/F005_BnF.Ar.329c-5-pre.json
#
# toy example:
#   $ cat ../../data/arabic/trans/foo-3-trans.xml | python isame_xml2txt.py |
#     tee ../../data/arabic/trans/foo-4.txt | python isame_parser.py |
#     tee ../../data/arabic/trans/foo-5-pre.json | python isame_mapper.py |
#     tee ../../data/arabic/trans/foo-6.json | python isame_json2tei.py > ../../data/arabic/trans/foo-7.xml
#
###############################################################################################################################################################################

import os
import re
import sys
import json
from io import TextIOBase
from bs4 import BeautifulSoup
from contextlib import ExitStack
from functools import singledispatch
from argparse import ArgumentParser, FileType

import logging
logging.basicConfig(handlers=[
                        logging.FileHandler(f'{os.path.splitext(os.path.basename(__file__))[0]}.log', mode='w',),
                        logging.StreamHandler()
                    ],
                    format='%(asctime)s :: %(levelname)s :: %(funcName)s :: %(lineno)d :: %(message)s',
                    level=logging.DEBUG)

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'local_settings.py')

#FIXME it might be that supplied text at the beginning of a page enters the last part of the notes of the previous page. Check!!
BLOCKS_REGEX = re.compile(r'(?P<title>TITLE:.+?)\n'
                          r'(?P<source>Source:.+?)\n'
                          r'(?P<content>.+?)'
                          r'(?P<notes>Notes:.+?)?(?=\nTITLE|$)', re.DOTALL)

LINE_REGEX = re.compile(r'((?:\( *)?\| *(?:-|[0-9]{1,2}) *\|(?: *\))?.*?)(?=(?:\( *)?\||$)', re.DOTALL)


def _xml2txt(infp, variants, rm_notes=False):
    """ convert content of archetype xml fp file to txt InterSaME format and write it in outfp.

    Args:
        infp (io.TextIOWrapper): xml input file resulted from Archetype.
        variants (list): list of variants read from settings file for Archetype transcription editor menus.
        rm_notes (bool): flag to indicate if notes tags and footnotes should be kept in conversion or not.

    Yield:
        tuple: title, source, content, notes of each image transcription found in infp.

    """
    xmltxt = infp.read()
    #xmltxt = BeautifulSoup(xmltxt, 'html5lib') #FIXME
    xmltxt = BeautifulSoup(xmltxt, 'lxml')


    # check there are *no* nested tags
    for child in xmltxt.recursiveChildGenerator():
        if child.name == 'span':
            for grand in child.find_all('span'):
                if grand.attrs == child.attrs:
                    print('Fatal error! Nested elements with the same tag were found and are not supported:',
                          child.name, child.attrs, file=sys.stderr)
                    sys.exit(1)

    # remove locus
    for elem in xmltxt.find_all("span", {"data-dpt" : "location", "data-dpt-loctype" : "locus"}):
        elem.replace_with('')

    # remove ref tags
    for elem in xmltxt.find_all("span", {"data-dpt" : "divider", "data-dpt-type" : "ref"}):
        elem.replaceWithChildren()

    # remove note tags and (if param on) them with plain text
    for elem in xmltxt.find_all("span", {"data-dpt" : "note_"}):
        if not rm_notes:
            elem.insert(0, '(')
            elem.append(')')
        elem.replaceWithChildren()

    # remove variant tags and mark them with plain text
    for struct, type_ in variants:
        for elem in xmltxt.find_all("span", {"data-dpt-type" : f'{struct}/{type_}'}):
            elem.insert(0, '[')
            elem.append(f'={struct}={type_}]')
            elem.replaceWithChildren()

    # remove supplied tags and them with plain text
    for elem in xmltxt.find_all("span", {"data-dpt" : "supplied_", "data-dpt-type" : "unclear"}):
        elem.insert(0, '{')
        elem.append('}')
        elem.replaceWithChildren()
    for elem in xmltxt.find_all("span", {"data-dpt" : "supplied_", "data-dpt-type" : "lacuna"}):
        elem.insert(0, '⟦')
        elem.append('⟧')
        elem.replaceWithChildren()
    for elem in xmltxt.find_all("span", {"data-dpt" : "supplied_", "data-dpt-type" : "illegible"}):
        elem.insert(0, '⟨')
        elem.append('⟩')
        elem.replaceWithChildren()

    # remove division tags and them with plain text
    for elem in xmltxt.find_all("span", {"data-dpt" : "divider", "data-dpt-type" : "fasila"}):
        if elem.text != '*':
            elem.insert(0, '*')
            elem.replaceWithChildren()
        #if elem.text in ('{*}', '⟨*⟩', '⟦*⟧'):
        #    elem.replaceWithChildren()
        #else:
        #    elem.insert(0, '*')
        #    elem.replaceWithChildren()
        #    #elem.replace_with(f'*{elem.text}') #FIXME

    for elem in xmltxt.find_all("span", {"data-dpt" : "divider", "data-dpt-type" : "awashir"}):
        if elem.text in ('{x}', '⟨x⟩', '⟦x⟧'):
            elem.replaceWithChildren()
        elif elem.text[0] == '+':
            elem.replace_with(f'+x{elem.text[1:]}')
        else:
            elem.replace_with(f'x{elem.text}')

    for elem in xmltxt.find_all("span", {"data-dpt" : "divider", "data-dpt-type" : "khawamis"}):
        if elem.text in ('{v}', '⟨v⟩', '⟦v⟧'):
            elem.replaceWithChildren()
        elif elem.text[0] == '+':
            elem.replace_with(f'+v{elem.text[1:]}')
        else:
            elem.replace_with(f'v{elem.text}')

    for elem in xmltxt.find_all("span", {"data-dpt" : "divider", "data-dpt-type" : "miaa"}):
        if elem.text in ('{c}', '⟨c⟩', '⟦c⟧'):
            elem.replaceWithChildren()
        elif elem.text[0] == '+':
            elem.replace_with(f'+c{elem.text[1:]}')
        else:
            elem.replace_with(f'c{elem.text}')

    ANY_BLOCK = False

    for block in BLOCKS_REGEX.finditer('\n'.join(xmltxt.strings)):

        ANY_BLOCK = True

        title = block.group('title').strip()
        source = block.group('source').strip()

        # if there is a supplied at the end, it can be known only by 2 newlines
        content_block, _, supplied = block.group('content').partition('\n\n')
        if '|' in supplied:
            print('block.group(content):  ' + block.group('content'), file=sys.stderr)
            print('content_block:  ' + content_block, file=sys.stderr)
            print('supplied:  ' + supplied, file=sys.stderr)
            print('Fatal error processing xml! There is a line in a separate paragraph.', file=sys.stderr)

        content = '\n'.join(li.replace(' ','').replace(chr(0xa0), '').strip() for li in LINE_REGEX.findall(content_block.replace('\n', ' ')))

        notes = ''
        if not rm_notes and block.group('notes'):
            notes = re.sub(r'\n+', '\n', block.group('notes').strip(), re.DOTALL)

        # fix annotation of multiple variants for the same text section
        content = content.replace(']=', ';')
        content = re.sub(r'\[+', '[', content)

        #print(xmltxt.prettify(), file=sys.stderr) #DEBUG

        yield title, source, content, notes

    if not ANY_BLOCK:
        print('Fatal error! No transcritions were found in this page. Check that the page template is correct.', file=sys.stderr) #TRACE

@singledispatch
def xml2txt(input_):
    raise NotImplementedError('Unsupported type')

@xml2txt.register(TextIOBase)
def _(input_, outfp, settingsfp=open(SETTINGS_PATH), rm_notes=False):
    """ convert content of archetype xml fp file to txt InterSaME format and write it in outfp.

    Args:
        _input (io.TextIOWrapper): xml input file resulted from Archetype.
        outfp (io.TextIOWrapper): output stream for storing txt InterSaME conversion.
        settingsfp (io.TextIOWrapper): settings file for Archetype transcription editor menus.
        rm_notes (bool): flag to indicate if notes tags and footnotes should be kept in conversion or not.

    Yield:
        tuple: title, source, content, notes of each image transcription found in infp.

    """
    #logging.debug(f"SETTINGS_PATH={SETTINGS_PATH}  VARIANTS={variants}") #DEBUG
    variants = [(str_, typ) for str_, typ in re.findall(f'\'(.+?)/(.+?)\'', settingsfp.read())]

    for title, source, content, notes in _xml2txt(input_, variants, rm_notes):
        print(f'{title}\n{source}\n{content}\n{notes}\n', file=outfp)

@xml2txt.register(list)
def _(input_, outfp, settingsfp=open(SETTINGS_PATH), rm_notes=False):
    """ convert content of archetype xml fp file to txt InterSaME format and write it in outfp.

    Args:
        input_ (list): grpup of xml input files(io.TextIOWrapper) resulted from Archetype.
        outfp (io.TextIOWrapper): output stream for storing txt InterSaME conversion.
        settingsfp (io.TextIOWrapper): settings file for Archetype transcription editor menus.
        rm_notes (bool): flag to indicate if notes tags and footnotes should be kept in conversion or not.

    Yield:
        tuple: title, source, content, notes of each image transcription found in infp.

    """
    #logging.debug(f"SETTINGS_PATH={SETTINGS_PATH}  VARIANTS={variants}") #DEBUG
    variants = [(str_, typ) for str_, typ in re.findall(f'\'(.+?)/(.+?)\'', settingsfp.read())]

    for infp in input_:
        for title, source, content, notes in _xml2txt(infp, variants, rm_notes):
            print(f'{title}\n{source}\n{content}\n{notes}\n', file=outfp)
    

if __name__ == '__main__':

    parser = ArgumentParser(description='convert xml archetype output to plain text in intersame format')
    parser.add_argument('--file', '-f', nargs='+', required=True, help='xml file(s)')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='text file with concatenated result of input files')
    parser.add_argument('--settings', type=FileType('r'), default=SETTINGS_PATH, help='local settings file for archetype')
    parser.add_argument('--rm_notes', action='store_true', help='remove note tags within the text')
    args = parser.parse_args()

    with ExitStack() as stack:
        fp_list = [stack.enter_context(open(fname)) for fname in args.file]
        xml2txt(fp_list, args.outfile, args.settings, args.rm_notes)

