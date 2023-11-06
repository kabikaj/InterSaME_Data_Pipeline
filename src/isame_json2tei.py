#!/usr/bin/env python3
#
#    isame_json2tei.py
#
# convert InterSaME transcription from json structure into xml TEI
#
# dependencies:
#  * List-of-manuscript-fragments.md
#
# TODO
#  * to_ara is not working well
#
# NOTES
#   * lb in our case is for line beginning, not line break
#   * for both lacuna and illegible, there are two possible tags depending if the text is given or not:
#       <supplied reason="lacuna">ما ننسـ</supplied>
#       <gap reason="lacuna" unit="rasm" extent="3"/>
#       <gap reason="lacuna" unit="rasm" atLeast="2" atMost="4"/>
#
#   <app>
#     <lem>العَذابِ</lem>
#     <rdg type="orthography" cause="alif,longA,fa'aal">
#        العذ
#     </rdg>
#   </app>
#
# exmaples:
#   $ cat testing_workflow/example_330b_3r-3v.json | python isame_json2tei.py > testing_workflow/example_330b_3r-3v.xml
#
#   $ cat ../../data/arabic/trans/BnF.Ar.330b-4.txt | python isame_parser.py | tee ../../data/arabic/trans/BnF.Ar.330b-5-pre.json | python isame_mapper.py |
#     tee ../../data/arabic/trans/BnF.Ar.330b-6.json | python isame_json2tei.py | tee ../../data/arabic/trans/BnF.Ar.330b-7.xml
#
#   $ cat ../../data/arabic/trans/foo-4.txt | python isame_parser.py | tee ../../data/arabic/trans/foo-5-pre.json | python isame_mapper.py |
#     tee ../../data/arabic/trans/foo-6.json | python isame_json2tei.py | tee ../../data/arabic/trans/foo-7.xml
#
#   $ cat ../../data/arabic/trans/F001-6.json | python isame_json2tei.py --sep " " --ara | grep -v "<!" > ../../data/arabic/trans/F001-7.xml
#
#   $ cat ../../data/arabic/trans/F001-4.txt | python isame_parser.py | tee ../../data/arabic/trans/F001-5-pre.json | python isame_mapper.py |
#     tee ../../data/arabic/trans/F001-6.json | python isame_json2tei.py | grep -v "<!" > ../../data/arabic/trans/F001-7.xml
#
###########################################################################################################################################################

import re
import os
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

from bs4 import BeautifulSoup, Comment
import xml.dom.minidom
import xml.parsers.expat
from xml.sax.saxutils import escape
from argparse import ArgumentParser, FileType
from itertools import chain, groupby

from rasm import rasm

from isame_util import HIST_ORIGIN, NUM_VERSES, SURA_NAMES, \
                       ARABIC_CHARS_MAPPING, ARABIC_MAPPING, ARABIC_CHARS_REGEX, ARABIC_REGEX, \
                       get_metadata_table, to_isame_trans

from isame_parser import FASILA_REGEX, AWASHIR_REGEX, KHAWAMIS_REGEX, HUNDRED_REGEX

MANUSCRIPT_TABLE_FILE = os.path.join(os.path.dirname(__file__), 'List-of-manuscript-fragments.md')
TEI_TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'TEI_TEMPLATE.xml')

RASM_DIACSET = '°²³¹ɂʔʷʸˀ˜ˢـᴬᴺᵃᵐᵒᵘᵚᵟᵢ•⁰ⁿ₁₂ₘₙₛ∴⌃⌄⒥⒧⒨⒬⒮'
DEFAULT_WORD_SEP = '#'

ESTIMATE_REGEX = re.compile(r'^(?P<min>[1-9][0-9]*)(?:-(?P<max>[1-9][0-9]*))?r')

class InterSaMETeiError(Exception):
    """ Error in TEI conversion.

    """
    pass

def calculate_fragments(struct, fgmts_table):
    """ prepare fragments information for tei header.

    Args:
        struct (list): json object containing all pages along with their editions.
        fgmts_table (dict): struture containing repositories information. It is created
            by the function util.get_metadata_table.

    Return:
        tuple: sequence of msFrag elements.

    """
    pages = [{'sig': p['meta']['signature'],
              'rep': fgmts_table[p['meta']['signature']]['Repository'],
              'fol': p['meta']['folio'],
              'loc': p['meta']['location']} for p in struct]


    out = []
    for sig, group in groupby(pages, key=lambda x: x['sig']):

        pages_gr = list(group)

        if len(pages_gr) == 1:
            summary = f'<summary>Contains f. {pages_gr[0]["fol"]}</summary>'
        else:
            summary = f'<summary>Contains ff. {pages_gr[0]["fol"]} to {pages_gr[-1]["fol"]}</summary>'

        out.append(f'''<msFrag>
                        <msIdentifier>
                          <settlement>{pages_gr[0]["loc"]}</settlement>
                          <repository>{pages_gr[0]["rep"]}</repository>
                          <idno>{sig}</idno>
                        </msIdentifier>
                        <msContents>
                          {summary}
                        </msContents>
                      </msFrag>''')

    return '\n'.join(out)

# <summary>
#   <p>Contains ff. {{INI}} to {{END}}</p>
#   <p>From Quran 2:134 to 2:277</p>
# </summary>

def create_responsabilities(struct, fgmts_table):
    """ Create the sequence of responsabilities according to the current historical item.

    Args:
        struct (list): transcription structure of all the historical manuscript.
        frgmts_table (dict): signature as key and a dict with all associated info as a value.
            Check util.get_metadata_table function.

    Return:
        str: xml object with the responsabilities for the current historical item.

    """    
    signatures = [(struct[i]['meta']['hist_id'], struct[i]['meta']['signature']) for i in range(len(struct))]

    edit_tran_revi = set((hist_id,
                          sig,
                          fgmts_table[sig]['Editor'],
                          fgmts_table[sig]['Transcriber'],
                          fgmts_table[sig]['Reviewer']) for hist_id, sig in signatures)

    responsib = []
    for hist_id, group in groupby(sorted(edit_tran_revi, key=lambda x: x[0]), key=lambda x: x[0]):
        frgmts = list(group)
        # editor
        if len(set(f[2] for f in frgmts))==1:
            responsib.append(f'''<respStmt>
                                   <resp>All fragments edited by</resp>
                                   <persName>{frgmts[0][2]}</persName>
                                 </respStmt>''')
        else:
            for f in frgmts:
                responsib.append(f'''<respStmt>
                                       <resp>Fragment {f[1]} edited by</resp>
                                       <persName>{f[2]}</persName>
                                     </respStmt>''')
        # transcriber
        if len(set(f[3] for f in frgmts))==1:
            responsib.append(f'''<respStmt>
                                   <resp>All fragments transcribed by</resp>
                                   <persName>{frgmts[0][3]}</persName>
                                 </respStmt>''')
        else:
            for f in frgmts:
                responsib.append(f'''<respStmt>
                                       <resp>Fragment {f[1]} transcribed by</resp>
                                       <persName>{f[3]}</persName>
                                     </respStmt>''')
        if len(set(f[4] for f in frgmts))==1:
            responsib.append(f'''<respStmt>
                                   <resp>All fragments reviwewed by</resp>
                                   <persName>{frgmts[0][4]}</persName>
                                 </respStmt>''')
        else:
            for f in frgmts:
                responsib.append(f'''<respStmt>
                                       <resp>Fragment {f[1]} reviwewed by</resp>
                                       <persName>{f[4]}</persName>
                                     </respStmt>''')    
    return '\n'.join(responsib)

def retrieve_text(blocks, inib, inic, endb, endc):
    """ get sequence of text within the indexes indicated

    Args:
        blocks(list): all block element
        inib(int): initial block
        inic(int): initial char
        endb(int): final block
        endc(int): final char

    return:
        str: tagged text.

    """
    retrieved = []
    blocks[inib]
    retrieved.append(blocks[inib]['tok'][inic:])
    for block in blocks[inib+1:endb]:
        retrieved.append(block['tok'])
    retrieved.append(blocks[endb]['tok'][:endc+1])

    return ''.join(retrieved)

def calculate_gap(end, start, include_first=True, include_last=True, sep=DEFAULT_WORD_SEP, diacritics=False):
    """ calculate the text between the end index and the start index.

    Quranic indexes follow the pattern (sura, vers, word, bloc).

    Args:
        end (int, int, int, int): quranic index where the previous transcription ended.
        tuple (int, int, int, int): quranic index where the next transcription starts.
        include_first (bool): include first block in the text of the gap.
        include_last (bool): include last block in the text of the gap.
        sep (str): word separator.

    Returns:
        str: text gap between the indexes

    """
    results = list(tks for _, tks in rasm((end, start), source='tanzil-uthmani', blocks=True, paleo=True))
    if not results:
        return

    if not include_first:
        if len(results[0])==1:
            results = results[1:]
        else:
            results[0] = results[0][1:]

    if not results:
        return

    if not include_last:
        if len(results[-1])==1:
            results = results[:-1]
        else:
            results[-1] = results[-1][:-1]        

    gap = sep.join(''.join(b[3] for b in toks) for toks in results)

    if diacritics:
        return to_isame_trans(gap)

    return re.sub(rf'[{RASM_DIACSET}]', '', gap)

def text_is_divider(text):
    """ check if text is a divider, i.e. fasila, kawamis, awashir or hundred.

    Utility function for converting transcription to Arabic characters but excluding dividers.

    Args:
        text (str): text to check.

    Return:
        bool: True if text is a divider, False otherwise.

    """
    return FASILA_REGEX.match('*'+text+'#') or KHAWAMIS_REGEX.match('v'+text+'#') or \
           AWASHIR_REGEX.match('x'+text+'#') or HUNDRED_REGEX.match('c'+text+'#') or \
           (text[0]=='+' and (KHAWAMIS_REGEX.match('v'+text[1:]+'#')) or AWASHIR_REGEX.match('x'+text[1:]+'#') or HUNDRED_REGEX.match('c'+text[1:]+'#'))


def prepare_content(page, folio, side, source, prev_page_end_qind=None, next_page_start_qind=None, sep='#', arabic=False, debug=False):
    """ convert the transcription contained in page into a TEI formatted object.

    Args:
        page (dict): stucture containing text and annotations.
        folio (str): folio number of the page.
        side (str): indication of the side of the ms: flesh or skin.
        source (str): web link of the image.
        prev_page_end_qind (tuple): index of final block of previous page or None if page is the first one.
        next_page_start_qind (tuple): index of strat block of next page or None if page is the last one.
        sep (str): word separator.
        arabic (bool): convert transcription into Arabic script.
        debug (bool): debug mode.

    Return:
        list: TEI tags and text.

    """
    content = []

    #
    # calculate posible gap and open sura and verse for first page
    #

    k = 0
    while not page['blocks'][k]['ind']:
        k += 1
    ini_qind = page['blocks'][k]['ind'][0]

    ini_sura, ini_vers, ini_word, ini_bloc = ini_qind

    if debug:
        logging.debug(f'@DEBUG@ $folio={folio} $prev_page_end_qind={prev_page_end_qind} ini_qind={ini_qind}')

    if not prev_page_end_qind:

        content.append(f'<div n="{ini_sura}" subtype="{SURA_NAMES[ini_sura]}" type="surah">')
        gap_found = False
        if ini_vers == 1:
            content.append(f'<ab n="1" type="ayah">')
        elif ini_vers == 2:
            content.append(f'<pb n="{folio}-"/>')
            content.append(f'<gap extent="1" reason="fragmWit" unit="ayah"/>')
            content.append(f'<ab n="2" type="ayah">')
            gap_found = True
        else:
            content.append(f'<pb n="{folio}-"/>')
            content.append(f'<gap extent="1-{ini_vers-1}" reason="fragmWit" unit="ayah"/>')
            content.append(f'<ab n="{ini_vers}" type="ayah">')
            gap_found = True
        if (gap := calculate_gap((ini_sura, ini_vers, 1, 1), (ini_sura, ini_vers, ini_word, ini_bloc), include_last=False, sep=sep)):
            if not gap_found:
                content.append(f'<pb n="{folio}-"/>')
            content.append(f'<supplied>{gap}</supplied>')

    #
    # calculate possible gap and change of verse, suras between pages, BEFORE PAGE BEGINS (-)
    #

    else:
        prev_page_sura, prev_page_vers, prev_page_word, _ = prev_page_end_qind

        if prev_page_sura == ini_sura:
            if prev_page_vers == ini_vers or prev_page_vers+1 == ini_vers:
                if (gap := calculate_gap(prev_page_end_qind, ini_qind, include_first=False, include_last=False, sep=sep)):
                    content.append(f'<pb n="{folio}-"/>')
                    content.append(f'<supplied>{gap}</supplied>')
            else:
                gap_found = False
                content.append('</ab>')
                if prev_page_vers+1 < ini_vers:
                    content.append(f'<pb n="{folio}-"/>')

                    extent = prev_page_vers+1 if prev_page_vers+2 == ini_vers else f'{prev_page_vers+1}-{ini_vers-1}'
                    content.append(f'<gap extent="{extent}" reason="fragmWit" unit="ayah"/>')

                    content.append(f'<ab n="{ini_vers}" type="ayah">')
                    gap_found = True
                if (gap := calculate_gap((ini_sura, ini_vers, None, None), ini_qind, include_last=False, sep=sep)):
                    if not gap_found:
                        content.append(f'<pb n="{folio}-"/>')
                    content.append(f'<supplied>{gap}</supplied>')
        else:
            content.append(f'<div n="{ini_sura}" subtype="{SURA_NAMES[ini_sura]}" type="surah">')
            content.append(f'<ab n="{ini_vers}" type="ayah">')
            gap_found = False
            if ini_vers != 1:
                gap_found = True
                content.append(f'<pb n="{folio}-"/>')
                extent = 1 if ini_vers == 2 else f'1-{ini_vers-1}'
                content.append(f'<gap extent="{extent}" reason="fragmWit" unit="ayah"/>')

            if (gap := calculate_gap((ini_sura, ini_vers, None, None), ini_qind, include_last=False, sep=sep)):
                if not gap_found:
                    content.append(f'<pb n="{folio}-"/>')
                content.append(f'<supplied>{gap}</supplied>')

    k = 0
    while not page['blocks'][k]['ind']:
        k += 1
    break_ = "no" if page['blocks'][k]['ind'][0][3] == 1 else "yes"

    content.append(f'<pb n="{folio}" facs="{source}" type="{side}"/>')

    prev_sura, prev_vers = None, None
    if prev_page_end_qind:
        cur_sura, cur_vers, cur_word, cur_bloc = prev_page_end_qind
    
    i, nblocks = -1, len(page['blocks'])
    while (i:=i+1) < nblocks:

        block = page['blocks'][i]
        if block['ind']:
            cur_sura, cur_vers, cur_word, cur_bloc = block['ind'][0]

        if prev_sura != None and prev_vers != None:
            if prev_sura != cur_sura:
                content.append('</ab>')
                content.append('</div>')
                content.append(f'<div n="{cur_sura}" subtype="{SURA_NAMES[cur_sura]}" type="surah">')
                content.append(f'<ab n="{cur_vers}" type="ayah">')
            elif prev_vers != cur_vers:
                content.append('</ab>')
                content.append(f'<ab n="{cur_vers}" type="ayah">')
        
        prev_sura, prev_vers = cur_sura, cur_vers

        for line in page['lines']:
            if line['inib'] == i:
                content.append(f'<lb n="{line["num"]}" break="{"no" if cur_bloc == 1 else "yes"}"/>')

        is_divider = False
        j, ntok = -1, len(block['tok'])
        while (j:=j+1) < ntok:

            #
            # open tags
            #

            #FIXME
            for note in page['notes']:
                if i == note['inib'] and j == note['inic']:
                    content.append(f'<note type="{note["type"]}">{note["note"]}</note>')

            # preliminary shape of variant:  [A/∅=vd=i‘rāb]  ->  <app>
            #                                                      <lem>∅</lem>
            #                                                      <rdg cause="i‘rāb" type="vd">A</rdg>
            #                                                    </app>
            for variant in page['variants']:
                if i == variant['inib'] and j == variant['inic']:
                    ref = variant["ref"]
                    _lay = variant['lay'] if variant['lay'] else ''
                    content.append(f"<app><lem>{ref}</lem><rdg type=\"{variant['stc']}\" cause=\"{variant['typ']}\" _lay=\"{escape(_lay)}\">")
                    break

            for unclear in page['unclear']:
                if i == unclear['inib'] and j == unclear['inic']:
                    content.append(f'<unclear>')
                    break

            for lacuna in page['lacunas']:
                if i == lacuna['inib'] and j == lacuna['inic']:
                    if (tagged_text := ESTIMATE_REGEX.match(retrieve_text(page['blocks'], *lacuna.values()))):
                        min_ = tagged_text.group('min')
                        if tagged_text.group('max'):
                            max_ = tagged_text.group('max')
                            content.append(f'<gap reason="lacuna" unit="rasm" atLeast="{min_}" atMost="{max_}"/>')
                            j += tagged_text.end()
                            for variant in page['variants']:
                                if illegible['endb'] == variant['endb'] and illegible['endc'] == variant['endc']:
                                    content.append(f'</rdg></app>')
                            break
                        else:
                            content.append(f'<gap reason="lacuna" unit="rasm" extent="{min_}"/>')
                            j += tagged_text.end()
                            for variant in page['variants']:
                                if illegible['endb'] == variant['endb'] and illegible['endc'] == variant['endc']:
                                    content.append(f'</rdg></app>')
                            break
                    else:
                        content.append('<supplied reason="lacuna">')
                    break

            for illegible in page['illegible']:
                if i == illegible['inib'] and j == illegible['inic']:
                    if (tagged_text := ESTIMATE_REGEX.match(retrieve_text(page['blocks'], *illegible.values()))):
                        min_ = tagged_text.group('min')
                        if tagged_text.group('max'):
                            max_ = tagged_text.group('max')
                            content.append(f'<gap reason="illegible" unit="rasm" atLeast="{min_}" atMost="{max_}"/>')
                            j += tagged_text.end()
                            for variant in page['variants']:
                                if illegible['endb'] == variant['endb'] and illegible['endc'] == variant['endc']:
                                    content.append(f'</rdg></app>')
                            break
                        else:
                            content.append(f'<gap reason="illegible" unit="rasm" extent="{min_}"/>')
                            j += tagged_text.end()
                            for variant in page['variants']:
                                if illegible['endb'] == variant['endb'] and illegible['endc'] == variant['endc']:
                                    content.append(f'</rdg></app>')
                            break

                    else:
                        content.append('<supplied reason="illegible">')
                    break
            
            #####################################################
            # START add char
            #####################################################

            # start dividers
            if i in page['fasilas'] and j == 0:
                content.append('<pc unit="fasila" pre="false">')
                is_divider = True
            if i in page['awashir'] and j == 0:
                content.append('<pc unit="awashir" pre="false">')
                is_divider = True
            if i in page['khawamis'] and j == 0:
                content.append('<pc unit="khawamis" pre="false">')
                is_divider = True
            if i in page['miaa'] and j == 0:
                content.append('<pc unit="miaa" pre="false">')
                is_divider = True

            if j < ntok:
                content.append(f'{block["tok"][j]}')

            # close divider
            if ((i in page['fasilas']) or (i in page['awashir']) or (i in page['khawamis']) or (i in page['miaa'])) and j == ntok-1:

                # do not close dividers yet in cases such as e.g. #*1DS{03}#, but close cases such as {*1DS03}
                within_unclear = False
                for unclear in page['unclear']:
                    if unclear['inib'] == i:
                        if unclear['inic'] == 0:
                            content.append('</pc>')
                            is_divider = False
                        within_unclear = True

                # do not close dividers in cases such as #+x1C+⟨C:90⟩#
                within_illegible = False
                for illegible in page['illegible']:
                    if illegible['inib'] == i:
                        if illegible['inic'] == 0 or illegible['endc'] < j:
                            content.append('</pc>')
                            is_divider = False
                        within_illegible = True

                if not within_unclear and not within_illegible:
                    content.append('</pc>')
                    is_divider = False

                #FIXME
                #elif within_illegible:
                #    # if illegible endc is not end of block, cases such as x1C+⟨1r⟩:60
                #    for illegible in page['illegible']:
                #        if illegible['endb'] == i:
                #            if illegible['endc'] != len(block['tok'])-1:
                #                content.append('</pc>')
                #                is_divider = False
                #            break

            #####################################################
            # END add char
            #####################################################
            
            #
            # close tags
            #
            
            for unclear in page['unclear']:
                if i == unclear['endb'] and j == unclear['endc']:
                    content.append(f'</unclear>')
                    # close now divider in cases such as e.g #*1DS{03}#
                    if is_divider:
                        content.append('</pc>')
                        is_divider = False
                    break

            for lacuna in page['lacunas']:
                if i == lacuna['endb'] and j == lacuna['endc'] and block["tok"][j] != 'r':
                    content.append(f'</supplied>')
                    break

            for illegible in page['illegible']:
                if i == illegible['endb'] and j == illegible['endc'] and block["tok"][j] != 'r':
                    content.append(f'</supplied>')
                    if is_divider and illegible['endc'] == ntok-1:
                        content.append('</pc>')
                        is_divider = False
                    break

            for variant in page['variants']:
                if i == variant['endb'] and j == variant['endc']:
                    content.append(f'</rdg></app>')
                    break

            #FIXME
            #for note in page['notes']:
            #    if i == note['endb'] and j == note['endc']:
            #        content.append(f'</note>')
            #        break

        if block['end']:
            content.append(sep)

    #
    # calculate posible gap and close sura and verse in the last page
    #

    if page['blocks'][-1]['ind']:
        end_qind = page['blocks'][-1]['ind'][-1]
        end_sura, end_vers, end_word, _ = end_qind
    else:
        end_qind = page['blocks'][-2]['ind'][-1]
        end_sura, end_vers, end_word, _ = end_qind

    if debug:
        logging.debug(f"@DEBUG@ $folio={folio} end_qind={end_qind} $next_page_start_qind={next_page_start_qind}")

    if not next_page_start_qind:

        gap_found = False
        if (gap := calculate_gap(end_qind, (end_sura, end_vers, None, None), include_first=False, sep=sep)):
            content.append(f'<pb n="{folio}+"/>')
            content.append(f'<supplied>{gap}</supplied>')
            gap_found = True
        content.append('</ab>')
        if end_vers == NUM_VERSES[end_sura]-1:
            if not gap_found:
                content.append(f'<pb n="{folio}+"/>')
            content.append(f'<gap extent="{NUM_VERSES[end_sura]}" reason="fragmWit" unit="ayah"/>')
        elif end_vers < NUM_VERSES[end_sura]-1:
            if not gap_found:
                content.append(f'<pb n="{folio}+"/>')
            content.append(f'<gap extent="{end_vers+1}-{NUM_VERSES[end_sura]}" reason="fragmWit" unit="ayah"/>')
        content.append('</div>')


    #
    # calculate possible gap and change of verse, suras between pages, AFTER PAGE END (+)
    #

    else:
        next_page_sura, next_page_vers, next_word, _ = next_page_start_qind
        if end_sura == next_page_sura:
            if end_vers == next_page_vers or end_vers+1 == next_page_vers:
                if (gap := calculate_gap(end_qind, next_page_start_qind, include_first=False, include_last=False, sep=sep)):
                    content.append(f'<pb n="{folio}+"/>')
                    content.append(f'<supplied>{gap}</supplied>')
            else:
                gap_found = False
                if (gap := calculate_gap(end_qind, (end_sura, end_vers+1, None, None), sep=sep)):
                    content.append(f'<pb n="{folio}+"/>')
                    content.append(f'<supplied>{gap}</supplied>')
                    gap_found = True
                content.append('</ab>')
                if not gap_found:
                    content.append(f'<pb n="{folio}+"/>')

                content.append(f'<gap extent="{end_vers+1}-{next_page_vers-1}" reason="fragmWit" unit="ayah"/>')
                content.append(f'<ab n="{next_page_vers}" type="ayah">')
        else:
            gap_found = False
            if (gap := calculate_gap(end_qind, (end_sura, end_vers, None, None), include_first=False, sep=sep)):
                content.append(f'<pb n="{folio}+"/>')
                content.append(f'<supplied>{gap}</supplied>')
                content.append('</ab>')
                gap_found = True

            # not last verse of sura
            if next_page_vers != NUM_VERSES[prev_sura]:
                if not gap_found:
                    content.append(f'<pb n="{folio}+"/>')

                extent = NUM_VERSES[prev_sura] if end_vers+1 == NUM_VERSES[prev_sura] else f'{end_vers+1}-{NUM_VERSES[prev_sura]}'
                content.append(f'<gap extent="{extent}" reason="fragmWit" unit="ayah"/>')
                content.append('</div>')

    if debug:
        return re.sub(r'\n+', r'\n', '\n'.join(re.sub(r'(<.+?>)', r'\1\n', ''.join(x))
            for x in [list(g) for _, g in groupby(content, key=lambda x: len(x)==1)]))
    else:
        return ''.join(content)

def post_process_variants(tei):
    """ adjust variant tags to their right shape.

    Args:
        tei (BeautifulSoup): tei document.

    """
    # // default  ->  <app>
    #                   <lem>∅</lem>
    #                   <rdg type="vd" cause="i‘rāb" _lay="^B">
    #                      A
    #                   </rdg>
    #                 </app>
    for var in tei.find_all('app'):

        lema = var.lem
        type_ = var.rdg['type']
        cause = var.rdg['cause']
        other_layers = var.rdg['_lay']
        first_layer = var.rdg.text

        # [A^B/∅=vd=i‘rāb]  ->  <app>
        #                         <lem>∅</lem>
        #                         <rdg cause="i‘rāb" type="vd" varSeq="1">A</rdg>
        #                         <rdg cause="i‘rāb" type="vd" varSeq="2">B</rdg>
        #                       </app>
        if other_layers.count('^') == 1:
            #var.rdg.decompose() #FIXME
            new_tag = tei.new_tag('rdg', type=type_, cause=cause, varSeq="1")
            new_tag.string = first_layer
            var.append(new_tag)
            new_tag = tei.new_tag('rdg', type=type_, cause=cause, varSeq="2")
            new_tag.string = other_layers[1:]
            var.append(new_tag)

        # [A&B/∅=vd=i‘rāb]  ->  <app>
        #                         <lem>∅</lem>
        #                         <rdg cause="i‘rāb" type="vd" varSeq="1">A</rdg>
        #                         <rdg cause="i‘rāb" type="vd" varSeq="1">B</rdg>
        #                       </app>
        elif other_layers.count('&') == 1:
            #var.rdg.decompose() #FIXME
            new_tag = tei.new_tag('rdg', type=type_, cause=cause, varSeq="1")
            new_tag.string = first_layer
            var.append(new_tag)
            new_tag = tei.new_tag('rdg', type=type_, cause=cause, varSeq="1")
            new_tag.string = other_layers[1:]
            var.append(new_tag)

        # [(ᵢ→&{ᵃ}&+ʷ)/ᵘ=vd=irab]  ->  <app>
        #                                <lem>ᵘ</lem>
        #                                <note type="reading">in lā yastawī ...</note>
        #                                <rdg cause="i‘rāb" type="vd" varSeq="1">ᵢ→</rdg>
        #                                <rdg cause="i‘rāb" type="vd" varSeq="1">{ᵃ}</rdg>
        #                                <rdg cause="i‘rāb" type="vd" varSeq="1">+ʷ</rdg>
        #                             </app>
        # 
        elif other_layers.count('&') == 2:
            #var.rdg.decompose() #FIXME
            # base layer
            new_tag = tei.new_tag('rdg', type=type_, cause=cause, varSeq="1")
            new_tag.string = first_layer
            var.append(new_tag)
            lay2, _, lay3 = other_layers[1:].partition('&')

            # second layer #FIXME processing of unclear
            new_tag = tei.new_tag('rdg', type=type_, cause=cause, varSeq="1")
            #m = re.search(r'.*?\{(.+?)\}.*', lay2)
            #if m:
            #    new_tag.string = re.sub(r'(.*?\{)(.+?)(\}.*?)', r'\1\3', lay2)
            #    inner_tag = BeautifulSoup(f'<unclear>{m.group(1)}</unclear>', 'lxml-xml')
            #    new_tag.find(text='{}').replace_with(inner_tag)
            #else:
            new_tag.string = lay2
            var.append(new_tag)

            # third layer
            new_tag = tei.new_tag('rdg', type=type_, cause=cause, varSeq="1")
            new_tag.string = lay3
            var.append(new_tag)

        # [A^∅>>B/A=vd=i‘rāb]  ->  <app>  // main and secondary readings / alternative (unequal coexistence)
        #                            <lem>A</lem>
        #                            <rdg cause="i‘rāb" type="vd" varSeq="1">A</rdg>
        #                            <rdg cause="i‘rāb" type="vd" varSeq="2">∅</rdg>
        #                            <rdg hand="#secondstage" cause="i‘rāb" type="vd">
        #                              <corr>B<corr/>
        #                            </rdg>
        #                          </app>
        #elif '^' in other_layers and '>>' in other_layers:
        #    ...

        # [A>>B/A=vd=i‘rāb]  ->  <app>
        #                          <lem>A</lem>
        #                          <rdg cause="i‘rāb" type="vd">A</rdg>
        #                          <rdg hand="#secondstage" cause="i‘rāb" type="vd">
        #                            <corr>B<corr/>
        #                          </rdg>
        #                       </app>
        elif other_layers.count('>') == 2:
            new_tag = tei.new_tag('rdg', type=type_, cause=cause, change="#secondstage")
            inner_new_tag = tei.new_tag('corr')
            inner_new_tag.string = other_layers[1:]
            new_tag.append(inner_new_tag)
            var.append(new_tag)

        # [A>?B/B=vd=i‘rāb]  ->  <app>
        #                          <lem>B</lem>
        #                          <rdg cause="i‘rāb" type="vd">A</rdg>
        #                          <rdg hand="#unclear" change="#firststage" cause="i‘rāb" type="vd">
        #                            <corr>B<corr/>
        #                          </rdg>
        #                        </app>
        elif '>?' in other_layers:
            new_tag = tei.new_tag('rdg', type=type_, cause=cause, change="#firststage", hand='#unclear')
            inner_new_tag = tei.new_tag('corr')
            inner_new_tag.string = other_layers[1:]
            new_tag.append(inner_new_tag)
            var.append(new_tag)

        # [A>B/B=vd=i‘rāb]  ->  <app>
        #                         <lem>B</lem>
        #                         <rdg cause="i‘rāb" type="vd">A</rdg>
        #                         <rdg change="#firststage" cause="i‘rāb" type="vd">
        #                           <corr>B<corr/>
        #                         </rdg>
        #                       </app>
        elif other_layers.count('>') == 1:
            new_tag = tei.new_tag('rdg', type=type_, cause=cause, change="#firststage")
            inner_new_tag = tei.new_tag('corr')
            inner_new_tag.string = other_layers[1:]
            new_tag.append(inner_new_tag)
            var.append(new_tag)

        del var.rdg['_lay']


    # convert text annotations inside corr and rdg to xml annotations
    for tag_name in ('corr', 'rdg'):
        for tag_ in tei.find_all(tag_name):

            if tag_.string:

                if '⟦' in tag_.string:
    
                    # <corr>           <corr>
                    #   ⟦ELBKM⟧   ->     <supplied reason="lacuna">ELBKM</supplied>
                    # </corr>          </corr>
                    inner_tag = BeautifulSoup(re.sub(r'⟦(.+)⟧', r'<supplied reason="lacuna">\1</supplied>', tag_.string), 'lxml-xml')
                    tag_.string = ''
                    tag_.append(inner_tag)
    
                elif '{' in tag_.string:
    
                    # <corr>           <corr>
                    #   {ELBKM}   ->     <unclear>ELBKM</unclear>
                    # </corr>          </corr>
                    inner_tag = BeautifulSoup(re.sub(r'\{(.+)\}', r'<unclear>\1</unclear>', tag_.string), 'lxml-xml')
                    tag_.string = ''
                    tag_.append(inner_tag)


def json2tei(infp,
             outfp,
             template = open(TEI_TEMPLATE_FILE).read(),
             sep = DEFAULT_WORD_SEP,
             to_ara = False,
             debug = False):
    """
    create conversion of InterSaME json into TEI and add metadata.

    Args:
        infp (io.TextIOWrapper): input json file.
        outfp (io.TextIOWrapper): output xml file.
        template (str): xml template for the tei.
        sep (str): word separator.
        to_ara (bool): if True, convert transcription to modern Arabic script.
        debug (bool): debug mode.

    """
    struct = json.load(infp)
    body = []
    nstruct = len(struct)

    for i, page in enumerate(struct):

        prev_qind, next_qind = None, None

        if i > 0:
            if struct[i-1]['page']['blocks'][-1]['ind']:
                prev_qind = struct[i-1]['page']['blocks'][-1]['ind'][-1]
            else:
                prev_qind = struct[i-1]['page']['blocks'][-2]['ind'][-1]

        if i < nstruct-1:
            k = 0
            while not struct[i+1]['page']['blocks'][k]['ind']:
                k += 1
            next_qind = struct[i+1]['page']['blocks'][k]['ind'][-1]

        body.append(prepare_content(page['page'],
                                    page['meta']['folio'],
                                    page['meta']['side'],
                                    page['meta']['source'],
                                    prev_qind,
                                    next_qind,
                                    sep,
                                    to_ara,
                                    debug))
    #
    # merge meta, text and tags
    #

    if debug:
        text_body = '\n'.join(body)
    else:
        text_body = ''.join(body)    

    fgmts_table = get_metadata_table(MANUSCRIPT_TABLE_FILE)
    inii = struct[0]['page']['blocks'][0]['ind'][0][:-2]
    if struct[-1]['page']['blocks'][-1]['ind']:
        endi = struct[-1]['page']['blocks'][-1]['ind'][-1][:-2]
    else:
        endi = struct[-1]['page']['blocks'][-2]['ind'][-1][:-2]
    
    MAPPING = {'{{HIST_ID}}': struct[0]['meta']['hist_id'],
               '{{BODY}}': text_body,
               '{{HIST_ORIGIN}}': HIST_ORIGIN[struct[0]['meta']['hist_id'][0]],
               '{{RESPONSABILITIES}}' : create_responsabilities(struct, fgmts_table),
               '{{INI_QINDEX}}': ':'.join(map(str, inii)),   #FIXME add all ranges
               '{{END_QINDEX}}': ':'.join(map(str, endi)),
               '{{SUPPORT}}': fgmts_table[struct[0]['meta']['signature']]['Support'],
               '{{INK}}': fgmts_table[struct[0]['meta']['signature']]['Ink'],
               '{{LEAF_DIMENSION}}': fgmts_table[struct[0]['meta']['signature']]['Leaf Dim.'],
               '{{LINES_PAGE}}': fgmts_table[struct[0]['meta']['signature']]['Lines per page'],
               '{{SCRIPT_STYPE}}': fgmts_table[struct[0]['meta']['signature']]['Script style'],
               '{{DATE}}': fgmts_table[struct[0]['meta']['signature']]['Start'],
               '{{FRAGMENTS}}': calculate_fragments(struct, fgmts_table),
    }

    REGEX = re.compile('|'.join(MAPPING))
    TEI = REGEX.sub(lambda m: MAPPING[m.group(0)], template)
    
    if debug:
        print(TEI) #TRACE https://www.liquid-technologies.com/online-xml-formatter

    else:
        try:
            xml.dom.minidom.parseString(TEI)
        except xml.parsers.expat.ExpatError as e:
            logging.error(f"Fatal error! malformed xml: {e}. Conversion stopped!")
            raise InterSaMETeiError
        soup = BeautifulSoup(TEI, 'lxml-xml')

        post_process_variants(soup)
        
        if to_ara:
            for elem in soup.find('body').find_all(text=True):
                text = elem.string.strip()
                if text:
           
                    # hack to exclude the dividers...
                    if text_is_divider(text):
                        continue

                    # remove pluses for consonantal diacritics
                    text = re.sub(r'([’,]+)\+([’,]+)', r'\2', text)
                    text = re.sub(r'(?<=[A-Y⇘⇐⇒⇓])\+([’,]+)', r'\1', text)

                    # perform Arabic conversion
                    text = ARABIC_CHARS_REGEX.sub(lambda m: ARABIC_CHARS_MAPPING[m.group(0)], text)
                    text = ARABIC_REGEX.sub(lambda m: ARABIC_MAPPING[m.group(0)], text)

                    elem.replace_with(text)

        # remove comments from template
        for element in soup(text=lambda s: isinstance(s, Comment)):
            element.extract()

        print(soup.prettify(), file=outfp)


if __name__ == '__main__':

    parser = ArgumentParser(description='convert InterSaME structure to xml TEI')
    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin, help='json file')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='xml file')
    parser.add_argument('--sep', default='#', help=f'word separator (default "{DEFAULT_WORD_SEP}")')
    parser.add_argument('--ara', action='store_true', help='convert transctiption into Arabic script')
    parser.add_argument('--debug', action='store_true', help='print xml as text for debugging')
    args = parser.parse_args()

    if args.ara and args.debug:
        print('Warning! --ara arg is incompatible with --debug', file=sys.stderr)

    try:
        json2tei(args.infile, args.outfile, sep=args.sep, to_ara=args.ara, debug=args.debug)
    except InterSaMETeiError:
        logging.error("TEI Conversion stopped!")
        sys.exit(1)
