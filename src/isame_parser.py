#!/usr/bin/env python
#
#    isame_parser.py
#
# parse transcription in InterSaME text format, check errors and convert it to InterSaME json format
#
# dependencies:
#   * intersame_indexes.json
#
# TODO
#   * add checking for unclears, etc not covering i:j indexes/ The only posibility are lacuna and w/o context ⟦i:j⟧
#     then the indexes for lacuna can be ⟦i:j-n:m⟧
#
# example:
#   $ cat ../../data/arabic/trans/BnF.Ar.330b-4.txt | python isame_parser.py > ../../data/arabic/trans/BnF.Ar.330b-5-pre.json
#
#   $ cat ../../data/arabic/trans/foo-4.txt | python isame_parser.py --debug | tee ../../data/arabic/trans/foo-5-pre.json | python isame_mapper.py |
#     tee ../../data/arabic/trans/foo-6.json | python isame_json2tei.py > ../../data/arabic/trans/foo-7.xml
#
#   $ cat ../../data/arabic/trans/BnF.Ar.330b-3-trans.xml | python isame_xml2txt.py --rm_note_tags | tee ../../data/arabic/trans/BnF.Ar.330b-4.txt |
#     python isame_parser.py | tee ../../data/arabic/trans/BnF.Ar.330b-5-pre.json | python isame_json2tei.py | tee ../../data/arabic/trans/BnF.Ar.330b-7.xml
#    cat ../../data/arabic/trans/F003_BnF.Ar.330b-3-trans.xml | python isame_xml2txt.py --rm_note_tags | tee F003_BnF.Ar.330b-4-trans.txt | python isame_parser.py | tee ../../data/arabic/trans/F003_BnF.Ar.330b-5-pre.json | python isame_json2tei.py | tee ../../data/arabic/trans/F003_BnF.Ar.330b-7.xml
#
############################################################################################################################################################

import os
import re
import sys
import logging
logging.basicConfig(handlers=[
                        logging.FileHandler(f'{os.path.splitext(os.path.basename(__file__))[0]}.log', mode='w',),
                        logging.StreamHandler()
                    ],
                    format='%(asctime)s :: %(levelname)s :: %(funcName)s :: %(lineno)d :: %(message)s',
                    level=logging.DEBUG)
try:
    import ujson as json
except ImportError:
    import json

from pprint import pprint #DEBUG
from argparse import ArgumentParser, FileType

from rasm import rasm

from isame_util import NUM_VERSES, ARCH, ARDW, NOTES_TAGS, EMPTY_SET, calculate_line, absent_text

class NoteError(TypeError):
    """Raised then notes information if not correct."""
    pass

class InterSaMESyntaxError(Exception):
    """ Exception for llegal syntax found in an InterSaME text document.

    """
    pass

PARSING_ERROR = False

ARCH = ARCH+EMPTY_SET

INDEXES_FILE = 'isame_indexes.json'

BLOCKS_REGEX = re.compile(r'TITLE:(?P<title>.+?)\n'
                          r'Source:(?P<source>.+?)\n'
                          r'(?P<trans>.+?)'
                          r'(?:Notes:\n(?P<notes>.+?))?(?=\nTITLE|$)', re.DOTALL)
# Origins of mss: (F)ustat, (D)amascus, (S)ana, (K)ayrawan, (U)nknown. S and K not included in InterSaME
TITLE_REGEX = re.compile(r'^([FDU][0-9]{3})_Q\.[0-9:\-]+?_(.+?)_(.+?)_f\.([0-9]{1,3}[rv])_((?:hair|flesh)\??|\?)$')
LINE_REGEX = re.compile(r'(?P<noteb>\()?\|(?P<n>-|[0-9]{1,2})\|\)?(?P<li>.*?)(?=(?:\()?\||$)', re.DOTALL)
ESTIMATE_REGEX = re.compile(r'^(?P<min>[1-9][0-9]*)(?:-(?P<max>[1-9][0-9]*))?r')

FASILA_REGEX = re.compile(r'^\*([1-9][0VHDCTSLO][\{⟨]?[0SOD][\{⟨]?[0-9][0-9][\}⟩]?'
                               r'(\+[0-9][0-9])?'
                               r'(?:\+[1-9][A-Z])?'
                               r'|∅)'
                               r'(?:[⟩⟧\}]?[#/>\)])')
                             
AWASHIR_REGEX  = re.compile(r'^x\+?[1-9][HARSLCPFO]'
                            r'(?:\+[1-9][A-Z])?'
                            r'(?:\+Q)?'
                            r'(?:\+[\{⟨]?([A-Y]{1,2}|[1-9](\-[1-9])?r)[\}⟩]?:[1-9][0-9]{0,2})?'
                            r'(?:[⟩⟧\}]?[#/>\)])')

KHAWAMIS_REGEX = re.compile(r'^v\+?[1-9][HARSLCPFO]'
                            r'(?:\+[1-9][A-Z])?'
                            r'(?:\+[\{⟨]?([A-Y]{1,2}|[1-9](\-[1-9])?r)[\}⟩]?:[1-9][0-9]{0,2})?'
                            r'(?:[⟩⟧\}]?[#/>\)])')

HUNDRED_REGEX =  re.compile(r'^c\+?[1-9][HARSLCPFO]'
                            r'(?:\+[1-9][A-Z])?'
                            r'(?:\+[\{⟨]?([A-Y]{1,2}|[1-9](\-[1-9])?r)[\}⟩]?:[1-9][0-9]{0,2})?'
                            r'(?:[⟩⟧\}]?[#/>\)])')

#FIXME
#SURA_DIV_0_1_REGEX = re.compile(r'^β([01])#?')
#SURA_DIV_2_REGEX = re.compile(r'^β2#?(?:(\+δ#?)|(δ#?))?')
#DECOR_REGEX = re.compile(r'^(\+δ#?)|(δ#?)')

VERSE_DIV_REGEX = re.compile(r'^([1-9][0-9]*):([1-9][0-9]*)#?')
VARIANT_REGEX = re.compile(r'/(?P<ref>.+?)=(?P<stc>.+?)=(?P<typ>.+?)]')

NOTES_REGEX = re.compile(r'\|L([0-9]{1,2})(?:-([0-9]{1,2}))?\.(.+?)\|(.+?)(?=\|L|$)', re.DOTALL)

DOTS_HAMZA_SET = 'ᵘᵢᵃaiuʷᴬˀ'

DOT_MISSING_REGEX = re.compile(r'[^ᵘᵢᵃaiuˀ\-!©↑↓↕←→↔≠][\-!©↑↓↕←→↔≠]+(?![1-9]r)')

# 
DOT_SEQ = re.compile(r'[ᵘᵢᵃaiuʷᴬ][^A-Y1-9ᵘᵃᵢaiuʷᴬ+#\[\{\}⟨―∅_)^]*')

# {ᵘ,ᵃ,ᵢ}©?{→,←,↔}{-,≠}{↑,↕,↓}! / {ᵘ,ᵃ,ᵢ}{→,←,↔}{-,≠}©?{↑,↕,↓}! / {ᵘ,ᵃ,ᵢ}{→,←,↔}{-,≠}{↑,↕,↓}!©?
DOT_SYNTAX = re.compile(r'^([ᵘᵢᵃaiuʷᴬ]©?(→{1,2}|←{1,2}|↔{1,2})?[\-≠]?(↑{1,2}|↓{1,2}|↕{1,2})?!{0,2}|'
                          r'[ᵘᵢᵃaiuʷᴬ](→{1,2}|←{1,2}|↔{1,2})?[\-≠]?©?(↑{1,2}|↓{1,2}|↕{1,2})?!{0,2}|'
                          r'[ᵘᵢᵃaiuʷᴬ](→{1,2}|←{1,2}|↔{1,2})?[\-≠]?(↑{1,2}|↓{1,2}|↕{1,2})?!{0,2}©?|'
                          r'ˀ[↑↕↓])$')

ERROR_DOT_SEQUENCES = ('ᵘ←', 'ᵃ-', 'ᵃ-!', 'ᵃ-↕!')


def parse_trans(title, folio, ini_index, trans, debug=False):
    """ prcess all information of a transcription of a manuscript image
    
    Args:
        title (str): image title. for debugging
        folio (str): folio of image, for debugging
        ini_index (int, int, int, int): index of first letterblock; sura, verse, word, block.
        trans (list): pairs of line info, line content that constitute the transcription of a manuscript image.
        debug (bool): show debugging info.

    Return:
        dict: parsed transcription

            /*
             * the annotations (i.e. unclear, illegible, etc) are inclusive, i.e. [i,j] means that i (pointer to beginning of block)
             * is the first bloc of the annotation and j (pointer to end of block) is the last bloc of the annotation.
             * The pointers are slices to the list of blocks and characters within the blocks.
             */

            struct = {
                "blocks"    : [{"tok"  : str,                    /* content of the block; variant info such as &^> might appear, as well as fasilas, etc, and estimatin of rasm letters such as 2-3r */
                                "ind"  : [(int, int, int, int)], /* sura, vers, word, bloc according to the Cairo Quran. These indexes start in 1. There might be an estimation due to lacunas and illegible */
                                "end"  : bool}, ...],            /* it indicates if it's last block of a word*/
                "lines"     : [{"num"  : float,                  /* line number: 1, 2, 3, ... or e.g. 1.5 is there is interlinear text between lines 1 and 2 */
                                "inib" : int}, ... ],            /* ptr to blocks where the line starts (inlusive) */
                "unclear"   : [{"inib" : int,                    /* { unclear }
                                "inic" : int,             
                                "endb" : int,             
                                "endc" : int}, ...],      
                "lacunas"   : [{"inib" : int,                    /* ⟦ lacuna ⟧ */
                                "inic" : int,             
                                "endb" : int,             
                                "endc" : int,             
                "illegible" : [{"inib" : int}, ...],             /* ⟨ illegible ⟩ */
                                "inic" : int,                    
                                "endb" : int,                    
                                "endc" : int}, ...],             
                "variants"  : [{"inib" : int,                    
                                "inic" : int,                    
                                "endb" : int,                    
                                "endc" : int,                    
                                "ref"  : str,                    /* reference text, i.e. Cairo Quran */
                                "stc"  : str,                    /* class of structure */
                                "typ"  : str,                    /* class of typology */
                                "lay"  : str}, ...],             /* other layers of text (&^>) */
                "fasilas"   : [int, ...],                        /* ptr to blocks where the fasila is located */
                "awashir"   : [int, ...],                        /* ptr to blocks where the awashir is located */
                "khawamis"  : [int, ...],                        /* ptr to blocks where the khawamis is located */
                "miaa"      : [int, ...],                        /* ptr to blocks where the miaa is located */
                "sura_div"  : [int, ...],                        /* ptr to blocks where the sura_div is located */
                "notes"     : [{"inib" : int,                      
                                "inic" : int,             
                                "endb" : int,             
                                "endc" : int,
                                "type" : str,  #FIXME there is a closed list of posibilities
                                "note" : str}, ...]             
            }

    #FIXME
    #Raise:
    #    SyntaxError: invalid syntax found in transcription.

    """
    global PARSING_ERROR

    if debug: logging.debug(f'title={title}')

    struct = {
        'blocks' : [],
        'lines' : [],
        'unclear' : [],
        'lacunas' : [],
        'illegible' : [],
        'variants' : [],
        'fasilas' : [],
        'awashir' : [],
        'khawamis' : [],
        'miaa' : [],
        'sura_div' : [],
        'notes' : [],
    }

    unclear = {'inib': None, 'inic': None, 'endb': None, 'endc': None}
    lacuna = {'inib': None, 'inic': None, 'endb': None, 'endc': None, }
    illegible = {'inib': None, 'inic': None, 'endb': None, 'endc': None}
    variant = {'inib': None, 'inic': None, 'endb': None, 'endc': None, 'ref': None, 'stc':None, 'typ': None}

    cur_isura, cur_ivers, cur_iword, cur_ibloc = ini_index
    current_block = []
    ini_bloc_line = ichar_ptr = 0
    ARDW_found = False
    variant_layers = None
    
    unclear_opened = lacuna_opened = illegible_opened = variant_opened = note_opened = False
    notes = [] # stack of notes
    notes_lines = [] # temporal data to store line notes, e.g. (|1|) 

    reading_fasila = reading_khawamis = reading_awashir = reading_miaa = reading_sura = False

    for iline in range(len(trans)):

        noteb, info_line, line = trans[iline]
        num_line = struct['lines'][-1]['num']+0.5 if info_line == '-' else int(info_line)
        if noteb:
            notes_lines.append(num_line)

        if debug:
            logging.debug(f'$num_line={num_line} $line={line}')

        i, n = -1, len(line)
        while (i:=i+1) < n:
            char = line[i]

            if debug:
                logging.debug(f'$char={char} $cur_ibloc={cur_ibloc} $ichar_ptr={ichar_ptr}')

            # skip sura info
            if char == '%':
                if reading_sura:
                    reading_sura = False
                else:
                    reading_sura = True
                continue
            elif reading_sura:
                continue

            if char == '*': reading_fasila = True
            if char == 'x': reading_awashir = True
            if char == 'v': reading_khawamis = True
            if char == 'c': reading_miaa = True

            #
            # variant
            #

            if char == '[':
                if variant['inib']:
                    logging.error(f'missing ] in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True
                variant_opened = True

            elif char in '>&^':
                if (m := re.search(f'[>&^][^(/)]+', line[i:])):
                    variant_layers = m.group(0)
                    
                    #DEPRECATED annotation on non-base layer will be stored in txt format
                    #if any(c in '⟨⟩⟦⟧{}' for c in variant_layers):
                    #    logging.error(f'illegal tag in variant correctoin "{title}". Corrections cannot include ⟨⟩⟦⟧{{}} tags. Stop parsing at [[{folio}.L{num_line}]]')
                    #    PARSING_ERROR = True
                    i += m.end()-1

            elif char == '/':
                if (m := VARIANT_REGEX.search(line[i:])):
                    variant['ref'] = m.group('ref')
                    variant['stc'] = m.group('stc')
                    variant['typ'] = m.group('typ')
                    variant['lay'] = variant_layers
                    i += m.end()-1
                    variant['endb'] = len(struct['blocks'])
                    variant['endc'] = ichar_ptr-1
                    if debug: logging.debug(f'@DEBUG:save:variant@ {variant}')
                    struct['variants'].append(variant)
                    variant = {'inib': None, 'inic': None, 'endb': None, 'endc': None, 'ref': None, 'stc':None, 'typ': None, 'lay': None}
                    variant_layers = None
                else:
                    logging.error(f'malformed variant in "{title}". The expected format is [A/B=D=C]. Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True
                variant_opened = False

            elif char == ']':
                #raise SyntaxError(f'malformed variant in "{title}". The expected format is [A/B=D=C]. Stop parsing at [[{folio}.L{num_line}]]') #FIXME
                logging.error(f'malformed variant in "{title}". The expected format is [A/B=D=C]. Stop parsing at [[{folio}.L{num_line}]]')
                PARSING_ERROR = True

            #
            # word
            #

            elif char == '#':

                if current_block:

                    if debug:
                        logging.debug(f'@DEBUG:save:1@ $tok={"".join(current_block)} $cur_isura={cur_isura} $cur_ivers={cur_ivers} $cur_iword={cur_iword} $cur_ibloc={cur_ibloc}')

                    if reading_fasila:
                        struct['fasilas'].append(len(struct['blocks']))
                        reading_fasila = False

                    if reading_awashir:
                        struct['awashir'].append(len(struct['blocks']))
                        reading_awashir = False

                    if reading_khawamis:
                        struct['khawamis'].append(len(struct['blocks']))
                        reading_khawamis = False

                    if reading_miaa:
                        struct['miaa'].append(len(struct['blocks']))
                        reading_miaa = False

                    struct['blocks'].append({'tok' : ''.join(current_block),
                                             'ind' : [(cur_isura, cur_ivers, cur_iword, cur_ibloc)],
                                             'end' : True})
                    current_block = []
                    cur_iword += 1
                    cur_ibloc = 1
                    ARDW_found = False
                ichar_ptr = 0
            
            elif char == '=':
                # allowed e.g. |L3|=LM... ; |L3|⟦=LM... ; |L3|{=LM...
                if i == 0 or (i == 1 and line[i-1] in ('⟦', '{', '(')) or re.match(r'^([^\]]+>)', line[:i-1]):
                    pass
                else:
                    logging.error(f'character = found in illegal position in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True

            #
            # notes
            #

            elif char == '(':
                notes.append({'inib': None, 'inic': None, 'endb': None, 'endc': None, 'type': None, 'note': None})
                note_opened = True
            
            elif char == ')':
                if not notes or notes[-1]['inib'] == None:
                    logging.error(f'missing ( in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True
                
                notes[-1]['endb'] = len(struct['blocks'])
                notes[-1]['endc'] = ichar_ptr-1

                if debug: logging.debug(f"@DEBUG:save:note@ {notes[-1]}")
                struct['notes'].append(notes[-1])
                notes.pop()

            #
            # unclear
            #

            elif char == '{':
                if unclear['inib']:
                    logging.error(f'missing }} in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True
                unclear_opened = True
            
            elif char == '}':
                if unclear['inib'] == None:
                    logging.error(f'missing {{ in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True
                
                unclear['endb'] = len(struct['blocks'])
                unclear['endc'] = ichar_ptr-1

                if debug: logging.debug(f"@DEBUG:save:unclear@ {unclear}")
                struct['unclear'].append(unclear)
                unclear = {'inib' : None, 'inic' : None, 'endb' : None, 'endc' : None}

            #
            # lacuna
            #
    
            elif char == '⟦':
                if lacuna['inib']:
                    logging.error(f'missing ⟧ in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True
                lacuna_opened = True

            elif char == '⟧':
                if lacuna['inib'] == None:
                    logging.error(f'missing ⟦ in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True

                lacuna['endb'] = len(struct['blocks'])
                lacuna['endc'] = ichar_ptr-1

                if debug: logging.debug(f"@DEBUG:save:lacuna@ {lacuna}")
                struct['lacunas'].append(lacuna)
                lacuna = {'inib' : None, 'inic' : None, 'endb' : None, 'endc' : None}
    
            #
            # illegible
            #

            elif char == '⟨':
                if illegible['inib']:
                    logging.error(f'missing ⟩ in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True
                else:
                    illegible_opened = True

            elif char == '⟩':
                if illegible['inib'] == None:
                    logging.error(f'missing ⟨ in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True

                illegible['endb'] = len(struct['blocks'])
                illegible['endc'] = ichar_ptr-1
                
                illegible['endc'] = ichar_ptr-1
                if debug: logging.debug(f"@DEBUG:save:illegible@ {illegible}")
                struct['illegible'].append(illegible)
                illegible = {'inib' : None, 'inic' : None, 'endb' : None, 'endc' : None}

            #
            # fasila  
            #

            elif char == '*' and line[i+1] not in '⟩⟧':
                if debug: logging.debug(f"@DEBUG:processing-fasila")
                if not FASILA_REGEX.search(line[i:]):
                    logging.error(f'invalid syntax following fasila * "{line[i:].partition("#")[0]}" in "{title}". Perhaps invalid variant or unclear instead of illegible? Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True
                continue

            #
            # awashir
            #

            elif char == 'x' and line[i+1] not in '⟩⟧':
                if not AWASHIR_REGEX.search(line[i:]):
                    logging.error(f'invalid syntax following awashir x "{line[i:].partition("#")[0]}" in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True
                continue

            #
            # khawamis
            #

            elif char == 'v' and line[i+1] not in '⟩⟧':
                if not KHAWAMIS_REGEX.search(line[i:]):
                    logging.error(f'invalid syntax following khawamis v "{line[i:].partition("#")[0]}" in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True
                continue

            #
            # miaa
            #

            elif char == 'c' and line[i+1] not in '⟩⟧':
                if not HUNDRED_REGEX.search(line[i:]):
                    logging.error(f'invalid syntax following miaa c "{line[i:].partition("#")[0]}" in "{title}". Stop parsing at [[{folio}.L{num_line}]]')
                    PARSING_ERROR = True
                continue

            elif char in '123456789' and not reading_fasila and not reading_khawamis and not reading_awashir and not reading_miaa and not ESTIMATE_REGEX.search(line[i:]):
                if (m := VERSE_DIV_REGEX.search(line[i:])):
                    cur_isura = int(m.group(1))
                    cur_ivers = int(m.group(2))+1
                    cur_iword = 1
                    cur_ibloc = 1
                    if cur_ivers == NUM_VERSES[cur_isura]+1:
                        cur_isura += 1
                        cur_ivers = 1
                        if cur_isura > 114:
                            logging.error(f'invalid sura number in "{title}": there are a total of 114 in the reference Quran. Stop parsing at [[{folio}.L{num_line}]]')
                    elif cur_ivers > NUM_VERSES[cur_isura]:
                        cur_isura = int(m.group(1))+1
                        cur_ivers = 1
                        logging.error(f'invalid verse number in "{title}": sura {cur_isura} has only {NUM_VERSES[cur_isura]} but {cur_ivers} found. Stop parsing at [[{folio}.L{num_line}]]')
                        PARSING_ERROR = True
                    i += m.end()-1
                else:
                    logging.error(f'invalid syntax in "{title}": unexpected number found. Stop parsing at [[{folio}.L{num_line}]]')
          
            else:
                # there can be something like ...W1-2r...
                if (char in ARCH or char in '123456789') and ARDW_found and current_block and not reading_fasila and not reading_awashir and \
                    not reading_khawamis and not reading_miaa:
                    if debug: logging.debug(f"@DEBUG:save:2@ $tok={''.join(current_block)} $cur_isura={cur_isura} $cur_ivers={cur_ivers} $cur_iword={cur_iword} $cur_ibloc={cur_ibloc}")
                    struct['blocks'].append(
                        {'tok' : ''.join(current_block),
                         'ind' : [(cur_isura, cur_ivers, cur_iword, cur_ibloc)],
                         'end' : False}
                    )
                    current_block = [char]
                    cur_ibloc += 1
                    ichar_ptr = 1
                    ARDW_found = False

                else:
                    current_block.append(char)
                    ichar_ptr += 1

                if char in ARDW:
                    ARDW_found = True

            #
            # update pointers for opening tags
            #

            if variant_opened and char not in '[{⟦⟨(=':
                variant['inib'] = len(struct['blocks'])
                variant['inic'] = ichar_ptr-1
                variant_opened = False
 
            if unclear_opened and char not in '{=[(':
                unclear['inib'] = len(struct['blocks'])
                unclear['inic'] = ichar_ptr-1
                unclear_opened = False
 
            if lacuna_opened and char not in '⟦=[(':
                lacuna['inib'] = len(struct['blocks'])
                lacuna['inic'] = ichar_ptr-1
                lacuna_opened = False
 
            if illegible_opened and char not in '⟨=[(':
                illegible['inib'] = len(struct['blocks'])
                illegible['inic'] = ichar_ptr-1
                illegible_opened = False

            if note_opened and char not in '(=[{⟦⟨':
                for j in reversed(range(len(notes))):
                    if notes[j]['inib'] == None:
                        notes[j]['inib'] = len(struct['blocks'])
                        notes[j]['inic'] = ichar_ptr-1
                    else:
                        break
                note_opened = False

        #
        # lines
        #

        struct['lines'].append({'num'  : num_line,
                                'inib' : ini_bloc_line})

        ini_bloc_line = len(struct['blocks']) if not current_block else len(struct['blocks'])+1


    # if a block remains, it's bc there is no final "#", so the block is not end of word
    if current_block:
        struct['blocks'].append({'tok' : ''.join(current_block),
                                 'ind' : [(cur_isura, cur_ivers, cur_iword, cur_ibloc)],
                                 'end' : False}
                                )

    struct['notes_lines'] = notes_lines

    return struct

def merge_notes(folio, parsed, footnotes, line_notes):
    """ add the notes information from footnotes and line_notes into parsed.

    Args:
        folio (str): folio being currently parsed (for debugging).
        parsed (dict): transcription structure. Each note in parsed['notes'] to modify has the following struct:
            {'inib': int, 'inic': int, 'endb': int, 'endc': int, 'line': float, 'type': None, 'note': None}
        footnotes (list of dicts): information of notes taken from the footnotes. Each item has the following format:
            {'iniline' : int, 'endline' : int, 'typenote' : str, 'textnote' : str}
        line_notes (lines): lines that are fully annotated.        

    Raise:
        NoteError: if there is a mismatch in the number of note annotations and footnotes.

    """
    NOTE_ERROR = False

    for lin in line_notes:
        parsed['notes'].append({'inib': -1, 'inic': -1, 'endb': -1, 'endc': -1, 'line': lin, 'note': None})

    if len(parsed['notes']) != len(footnotes):
        logging.error(f'Mismatch in the number of note annotations and footnotes in {folio}')
        NOTE_ERROR = True

    for noteann, footnote in zip(sorted(parsed['notes'], key=lambda x: (x['line'], x['inib'], x['inic'], x['endb'], x['endc'])), footnotes):
        
        noteann['type'] = footnote['typenote']
        noteann['note'] = footnote['textnote']

        if noteann['inib'] == -1:
            nlines = len(parsed['lines'])
            for i in range(nlines):
                noteann['inib'] = parsed['lines'][i]['inib']
                if parsed['lines'][i]['num'] == noteann['line']:
                    break
            noteann['inic'] = 0

            for i in range(nlines):
                if parsed['lines'][i]['num'] == footnote['endline']:
                    break

            # note goes until last block of page
            if i == nlines-1:
                noteann['endb'] = len(parsed['blocks'])-1
            else:
                noteann['endb'] = parsed['lines'][i+1]['inib']-1

            noteann['endc'] = len(parsed['blocks'][noteann['endb']]['tok'])-1

        if noteann['line'] != footnote['iniline']:
            noteann_cut = dict(noteann)
            noteann_cut['note'] = noteann_cut['note'][:min(20, len(noteann_cut['note']))]+' ...'
            footnote_cut = dict(footnote)
            footnote_cut['textnote'] = footnote_cut['textnote'][:min(20, len(footnote_cut['textnote']))]+' ...'
            logging.error(f'noteann "{noteann_cut}" and footnote "{footnote_cut}" refer to different lines')
            NOTE_ERROR = True

        del noteann['line']

    if NOTE_ERROR:
        raise NoteError(f'error parsing notes')

def check_dots(token, title, folio, lines, curbloc, level='error'):
    """
    Args:
        token (str): token to parse.
        title (str): title of token to parse.
        folio (str): folio of token to parse.
        lines (list): struct containing lines info.
        curbloc (int): current block.

    Return:
        bool: False if token has a dot sequence with incorrect syntax, True otherwise.

    """
    if not token:
        return False

    if level not in ('error', 'warning'):
        level = 'error'

    ERROR_FOUND = False

    # we don't check - because it can be part of i-jr
    # Be aware that the hamza has arrows too: ˀ↑, ˀ↕, ˀ↓
    if (dot_miss := DOT_MISSING_REGEX.search(token)):
        logging.error(f'Fatal error: dot attribute symbols "{dot_miss.group(0)}" found without any preceding ᵘᵢᵃ in '
                      f'"{title}" tok="{token}" [[{folio}.L{calculate_line(lines, curbloc)}]]')
        ERROR_FOUND = True

    if token[0] in DOTS_HAMZA_SET:
        logging.warning(f'Warning: dot/hamza at the beginning of token in '
                      f'"{title}" tok="{token}" [[{folio}.L{calculate_line(lines, curbloc)}]]') 

    for dot_error in ERROR_DOT_SEQUENCES:
        if dot_error in token:
            logging.warning(f'Fatal error: token has erroneous dot sequence in '
                          f'"{title}" tok="{token}" [[{folio}.L{calculate_line(lines, curbloc)}]]')
        
    if any(re.search(rf'{s}[A-Y]', token) for s in ('ᵘᵘ', 'ᵃᵃ', 'ᵢᵢ')):
        logging.error(f'Fatal error: invalid sequence ᵘᵘ, ᵃᵃ or ᵢᵢ in '
                      f'"{title}" tok="{token}" [[{folio}.L{calculate_line(lines, curbloc)}]]')
        ERROR_FOUND = True

    # notice the defaults:
    #    ᵘ: by default baseline, attached and left
    #    ᵢ: by default below the baseline, attached and centre
    #    ᵃ: by default above the baseline, attached and centre
    if any(d in  token for d in DOTS_HAMZA_SET):

        for dot in DOT_SEQ.findall(token):
            #print(f'~/DEBUG/~ dot="{dot}"', file=sys.stderr) #DEBUG
            if not DOT_SYNTAX.match(dot) or dot.count('©')>1:
                if '.' in dot:
                    logging.warning(f'Possible invalid dot syntax "{dot}" in "{title}" tok="{token}" [[{folio}.L{calculate_line(lines, curbloc)}]]')
                else:
                    if level == 'error':
                        logging.error(f'Fatal error: invalid dot syntax "{dot}" in "{title}" tok="{token}" [[{folio}.L{calculate_line(lines, curbloc)}]]')
                        ERROR_FOUND = True
                    elif level == 'warning':
                        logging.warning(f'Warning: possible invalid dot syntax "{dot}" in "{title}" tok="{token}" [[{folio}.L{calculate_line(lines, curbloc)}]]')
    
    return ERROR_FOUND

def parse(infp, outfp, index_fname=INDEXES_FILE, no_dot_check=False, debug=False):
    """ parse infp text file and conevrt it into a json document.

    Args:
        infp (io.TextIOWrapper):
        outfq (io.TextIOWrapper):
        index_fname (str): name of json file contaning quran indexes. #FIXME deberias quitarlo de aqui y usarlo solo en el mapper
        no_dot_check (bool): do not check the dots.
        debug (bool): show debugging info.

    Raise:
        InterSaMESyntaxError: if InterSaME txt document is malformed.

    """
    global PARSING_ERROR

    with open(index_fname) as index_fp:
        indexes = json.load(index_fp)

    text = infp.read()

    blocks = list(BLOCKS_REGEX.finditer(text))
    
    if len(blocks) != len(re.findall(r'TITLE:', text, re.DOTALL)):
        logging.error("Fatal error: one or more blocks not recognised in file")
        PARSING_ERROR = True
        

    # we need to have a list because a hist-id can have more than one fragments
    out = []
    for block in blocks:
        
        title = block.group('title').strip()
        source = block.group('source').strip()
        trans = block.group('trans').strip()
        notes = block.group('notes')

        if not (title_parsed := TITLE_REGEX.match(title)):
            logging.error(f"Fatal error: invalid syntax for title \"{title}\"")
            PARSING_ERROR = True
            hist_id, loc, sig, folio, side = 5*(None,)
        else:
            hist_id, loc, sig, folio, side = title_parsed.groups()

        try:
            ini = indexes[hist_id][sig][folio]
        except KeyError:
            logging.error(f"Fatal error: start index not found in index file for hist_id=\"{hist_id}\" sig={sig} folio={folio}")
            PARSING_ERROR = True
            ini = 4*(-1,)

        meta = {'title' : title,
                'hist_id' : hist_id,
                'location' : loc,
                'signature' : sig,
                'folio' : folio,
                'side' : side,
                'ini_index' : ini,
                'source' : source}

        if debug:
            logging.debug(f"$hist_id={hist_id} $location={loc} $signature={sig} $folio={folio} $side={side} "
                          f"$START={ini} $source={source}")

        lines = [LINE_REGEX.match(line) for line in filter(None, trans.replace('\r\n', '\n').split('\n'))]

        if not all(lines):
            logging.error(f"Fatal error: invalid syntax for one or more lines in \"{title}\"")
            PARSING_ERROR = True
            
        # check empty lines
        for i, (j, li) in enumerate(((l.group('n'), l.group('li')) for l in lines), 1):
            if not li and len(lines)==i-1:
                logging.error(f"Fatal error: invalid syntax for line in \"{title}\" [[{folio}.L{j}]]")
                PARSING_ERROR = True
                
            
        # check line numbers that don't match, exclusing -
        for i, (j, li) in enumerate([(l.group('n'), l.group('li')) for l in lines if l.group('n')!='-'], 1):
            if i != int(j):
                logging.error(f"Fatal error: invalid line number for line in \"{title}\" [[{folio}{side}.L{j}]]")
                PARSING_ERROR = True
                

        # check a lacuna is not surrounding an index in the whole text (it may be covering several lines)
        if re.search(r'⟦[^⟦]+?#\d+:\d+#[^⟦]+?⟧', ''.join(l.group('li') for l in lines)):
            logging.error(f"Fatal error: a lacuna cannot include a Quranic index \"{title}\" [[{folio}.L?]]")
            PARSING_ERROR = True
            

        for j, li in ((l.group('n'), l.group('li')) for l in lines):
            # check there are no spaces
            if ' ' in li:
                logging.error(f'Fatal error: space found in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True
                
            # check there are no multiple # together
            if '##' in li:
                logging.error(f'Fatal error: concatenated # found in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True
                
            # check there are no opening tags at the end of a line
            if li and li[-1] in ('{', '⟦', '⟨', '['):
                logging.error(f'Fatal error: opening {{, ⟦, ⟨ or [ found at the end of line in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True
                
            # check there are no closing tags after a word separator, i.e. #}
            if re.search(r'#[\}⟧⟩\]]', li):
                logging.error(f'Fatal error: closing tag }}, ⟧, ⟩ or ] found just after a word separator in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True
                
            # check there are no NQY in non-final positions (the checking is done only in the first hand!)
            if re.search(fr'[NQY][^#]*[{ARCH}]', re.sub(r'\[(.+?)(?:[>^&].*?)*/.+?\]', r'\1', li)):
                logging.warning(f'Warning: there might be N, Q or Y in non-final position in "{title}" [[{folio}.L{j}]]')
                #PARSING_ERROR = True
                
            # check ther are no letterblocks splited between two lines
            if re.search(rf'[BGSCTEFQKLMNHY][^{ARCH}#=]*$', li):
                logging.error(f'Fatal error: letterblock splitted between two lines "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True
                
            # check an index is always surrounded by hashtag
            if re.search(r'[^#\d]\d+:\d+#|#\d+:\d+[^#\d]', li):
                logging.error(f'Fatal error: an index must always be surrounded by # "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True
                
            # check reference is not empty
            if '/=' in li:
                logging.error(f'Fatal error: reference text empty ("/=") in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True

            # check fasila containing empty set is marked with the corresponding subdivision
            # [∅>*1CD07/*=sub=fasila], [*∅>*1VO05/*=sub=fasila] are wrong
            if re.search(r'\[∅(>\*[0-9A-Z]{5})?/\*=sub=fasila\]', li) or re.search(r'\[*∅>*[0-9A-Z]{5}/*=sub=fasila\]', li):
                logging.error(f'Fatal error: subdivision variant without marking the fasila in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True

            # note after correction e.g. [BEFLWN>B+’’EFLWN(ᵃ←!)/B’’ᵃE’ᵒF’ᵘLᵘWN’ᵃ=r=mech.haplog] is ILLEGAL
            if (m:=re.search(r'[>&\^][^/]*[()]', li)):
                logging.error(f'Fatal error: Note tags cannot appear after a > & or ^, "{m.group()}" in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True

            # note within reference text
            if (m:=re.search(r'/[^=]*[()]', li)):
                logging.error(f'Fatal error: Note tags cannot appear within the reference text, "{m.group()}" in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True

            # closing unclear inside correction, e.g. [{ᵃ→↕>ᵃ©←↑}/ˀᵃ=vd=hamza] is ILLEGAL, but [ᵃ→↕>ᵃ{©←↑}/ˀᵃ=vd=hamza] is LEGAL
            if (m:=re.search(r'>[^/{]*}', li)):
                logging.error(f'Fatal error: unclear closing tag cannot be inside a correction, unless the opening tag is also within the correction,'
                              f' "{m.group()}" in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True
            # closing illegible inside correction
            if (m:=re.search(r'>[^/⟨]*\⟩', li)):
                logging.error(f'Fatal error: illegible closing tag cannot be inside a correction, unless the opening tag is also within the correction,'
                              f' "{m.group()}" in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True
            # closing lacuna inside correction
            if (m:=re.search(r'>[^/⟦]*\⟧', li)):
                logging.error(f'Fatal error: lacuna closing tag cannot be inside a correction, unless the opening tag is also within the correction,'
                              f' "{m.group()}" in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True

            # if a divider is unclear, illegible or lacuna, the mark must cover the divider and not the other way round
            # e.g. *{1DS03} is wrong  /  {*1DS03} is right
            if re.search(r'[*xvc][\{⟨⟦(]', li):
                logging.error(f'Fatal error: unclear/illegible/lacuna/note must be outside the divider (fasila, khawamis, awashir, miaa)'
                              f', so e.g. {{*...}} is correct, *{{...}} is not, in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True

            # missing variant brackets, e.g. |2|=MA#LHMᵘ←/ᵒ#
            if re.search(r'^[^\[]+?/', li):
                logging.error(f'Fatal error: variant without brackets in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True

        # check when a line does not end in # the following starts with =
        for k, (j, li) in enumerate((l.group('n'), l.group('li')) for l in lines[:-1]):
            final_hashtag = re.search(r'#(?:(=.+?=.+?(;.+?=.+?)*\])|⟧)?$', li)
            next_initial_equal = re.search(r'^(?:([^\]]+>)|⟦)?=', lines[k+1].group('li'))
            if not final_hashtag and not next_initial_equal:
                logging.error(f'Fatal error: line missing final # or next line missing = in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True
                
            if final_hashtag and next_initial_equal:
                logging.error(f'Fatal error: line ending in # and next line ending in = in "{title}" [[{folio}.L{j}]]')
                PARSING_ERROR = True
                

        # check if Quran ref starts in block 1 and the first line has an equal
        if re.match(r'\(?=', lines[0].group('li')):
            if ini[3] == 1:
                logging.error(f'Fatal error: block inicated as 1 and first line starts with = in "{title}" [[{folio}.L1]].')
                PARSING_ERROR = True
                
        # check if Quran ref do not start in block 1 and the first line does not have an equal
        else:
            if ini[3] != 1:
                logging.error(f'Fatal error: block is not 1 and first line does not start with = in "{title}" [[{folio}.L1]].')
                PARSING_ERROR = True
                

        #======================
        # process transcription
        #======================

        sura_vers_marks = re.findall(r'\d{1,3}:\d{1,3}', ''.join(li.group('li') for li in lines))

        if sura_vers_marks:
            sura_end, vers_end = sura_vers_marks[-1].split(':')
        else:
            sura_end, vers_end = ini[0], ini[1]

        try:
            parsed = parse_trans(title, folio, ini, [line_regex.groups() for line_regex in lines], debug)
        except (SyntaxError, IndexError) as err:
            logging.error(f'Fatal error: {err}')
            PARSING_ERROR = True

        if notes:
            found_notes = [{'iniline': int(inili),
                            'endline': int(endli) if endli else None,
                            'typenote': typen,
                            'textnote': textn.strip()} for inili, endli, typen, textn in NOTES_REGEX.findall(notes)]

            for n in parsed['notes']:
                n['line'] = calculate_line(parsed['lines'], n['inib'])

            try:
                merge_notes(folio, parsed, found_notes, parsed["notes_lines"])
                del parsed['notes_lines']
            except NoteError as err:
                logging.error(f'Fatal error: {err}')
                PARSING_ERROR = True

        out.append({'meta' : meta, 'page' : parsed})

    #
    # check transcription encoding
    #

    for item in out:

        title = item['meta']['title']
        folio = item['meta']['folio']
        lines = item['page']['lines']

        for i, block in enumerate(item['page']['blocks']):

            tok = block['tok']

            if (m := re.search(r'(Y)(?![⇓⇒])', block['tok'])):
                if not absent_text(i, m.span()[0], item['page']['illegible'], item['page']['lacunas']):
                    logging.warning(f'Warning: Y found without ⇓⇒ in "{title}" tok="{tok}" [[{folio}.L{calculate_line(lines, i)}]]')

            if any(s in tok for s in ('Y→', 'Y↓', 'G←', 'G↘', 'ˀ˦', 'ˀ˥')):
                logging.error(f'Fatal error: illegal Y or G shape symbol or ˀ in "{title}" tok="{tok}" [[{folio}.L{calculate_line(lines, i)}]]')
                PARSING_ERROR = True
                
            if not no_dot_check and check_dots(tok, title, folio, lines, i):
                PARSING_ERROR = True

            if not no_dot_check and any(s in tok for s in 'ᵟᵒ°ᵐ'):
                logging.error(f'Fatal error: any of ᵟᵒᵐᵚ found in "{title}" tok="{tok}" [[{folio}.L{calculate_line(lines, i)}]]')
                PARSING_ERROR = True
                        
        for var in item['page']['variants']:
            if var['lay'] and (m := re.search(r'(Y)(?![⇓⇒])', var['lay'])):
                    if not absent_text(i, m.span()[0], item['page']['illegible'], item['page']['lacunas']):
                        logging.warning(f'Warning: Y found without ⇓⇒ in "{title}" tok="{tok}" [[{folio}.L{calculate_line(lines, i)}]]')
            if not no_dot_check and check_dots(var['lay'], title, folio, lines, var['inib'], level='warning'):
                PARSING_ERROR = True
                
    if PARSING_ERROR:
        raise InterSaMESyntaxError('parsing error!')

    json.dump(out, outfp, ensure_ascii=False, indent=4)


if __name__ == '__main__':

    parser = ArgumentParser(description='parse transcription in InterSaME text format and convert to InterSaME json format')
    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin, help='text file')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='json file')
    parser.add_argument('--indexes', default=INDEXES_FILE, help='json file with start qindexes')
    parser.add_argument('--no_dot_check', action='store_true', help='do not check dot system')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    args = parser.parse_args()

    try:
        parse(args.infile, args.outfile, args.indexes, args.no_dot_check, args.debug)
    except (KeyError, InterSaMESyntaxError) as e:
        logging.error(f'Parsing aborted! "{e}"')
        sys.exit(1)

