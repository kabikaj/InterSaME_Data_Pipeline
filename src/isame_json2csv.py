#!/usr/bin/env python
#
#    isame_json2csv.py
#
# get list of tokens from InterSaME json that are not illegible nor lacuna and convert them to tabular
# form along with their Quranic index and modern part-of-speeches.
#
# illegibleor lacuna sections ar marked with *
# unclear sections are marked between {}
#
# TODO
# ----
#   - think how to show the different layers of script. now we are only showing the first one
#   - corrections in a special column?
#   - remove signature in column and title!!!
#
# example:
#   $ cat ../../data/arabic/trans/F001-6.json | python isame_json2csv.py > ../../data/arabic/trans/F001.csv
#
##############################################################################################################

import os
import re
import sys
from argparse import ArgumentParser, FileType
try:
    import ujson as json
except ImportError:
    import json

from rasm import rasm

from isame_util import calculate_line, to_isame_trans

MYPATH = os.path.abspath(os.path.dirname(__file__))
DT_QURAN_FNAME = os.path.join(MYPATH, '../../../../abjad_util/data/processed/mushaf.json')

SEP = '#'
ASTERIX_REGEX = re.compile(r'(?<=\*)\*+')
ESTIMATE_REGEX = re.compile(r'[1-9](\-[1-9])?r')
NORM_ASTERISK_REGEX = re.compile(r'\*+')

# for catching illegible/lacuna sections in non-base layers
LACUNA_ILLEGIBLE_REGEX = re.compile(r'⟦.+⟧|⟨.+⟩')

def calculate_absent(pos, tok, lacunas, illegible, unclear, limit_inic=None, limit_endc=None):
    """ remove lacunas and illegible from tok and fill the missing parts with *.
    Mark unclear sections with {}.

    Args:
        pos (int): ndex of token tok.
        tok (str): token to modify.
        lacunas (list): list of lacuna elements.
        illegible (list): list of illegible elements.
        unclear (list): list of unclear elements.
        limit_inic (int): offset to initial character form block to show in results, None if not applicable.
        limit_endc (int): offset to final character form block to show in results, None if not applicable.

    Return:
        srt: modified string

    """
    new_tok = []
    for i, c in enumerate(tok):

        if limit_inic and i < limit_inic:
            continue

        if limit_endc and i > limit_endc:
            continue

        for lac in lacunas:
            if lac['inib'] == pos:
                if lac['endb'] == pos:
                    if lac['inic'] <= i and lac['endc'] >= i:
                        c = '*'
                        continue
                elif lac['endb'] > pos:
                    if lac['inic'] <= i:
                        c = '*'
                        continue
            elif lac['inib'] < pos:
                if lac['endb'] == pos:
                    if lac['endc'] >= i:
                        c = '*'
                        continue
                elif lac['endb'] > pos:
                    c = '*'
                    continue

        for ill in illegible:
            if ill['inib'] == pos:
                if ill['endb'] == pos:
                    if ill['inic'] <= i and ill['endc'] >= i:
                        c = '*'
                        continue
                elif ill['endb'] > pos:
                    if ill['inic'] <= i:
                        c = '*'
                        continue
            elif ill['inib'] < pos:
                if ill['endb'] == pos:
                    if ill['endc'] >= i:
                        c = '*'
                        continue
                elif ill['endb'] > pos:
                    c = '*'
                    continue
        
        for unc in unclear:
            if unc['endb'] == pos and unc['endc'] == i:
                c = c+'}'
            if unc['inib'] == pos and unc['inic'] == i:
                c = '{'+c

        new_tok.append(c)

    return ASTERIX_REGEX.sub('', ''.join(new_tok)).replace('∅', '')

def contains_disagr(pos, tok, page):
    """ calculate if block at index pos contains a disagreement.

    Args:
        pos (int): position of block token.
        tok (str): original block.
        page (dict): page structure.

    Return:
#FIXME
        str, str: the first element is 1 if block at pos contains a variant, 0 otherwise. If there is a disagreement,
            the second returned variable contains the base layer followed by '>' and the disagreement text.

    """
    for var in page['variants']:
        if var['inib'] <= pos and var['endb'] >= pos:
            if (corr := var['lay'].replace('#', ' ') if var['lay'] else ''):

                # [...ABC...]
                if var['inib'] < pos and var['endb'] > pos:
                    disagr_txt = corr
    
                # A[B]C
                elif var['inib'] == pos and var['endb'] == pos:
                    disagr_txt = tok[:var['inic']] + corr + tok[var['endc']+1:]
                
                # A[BC... #FIXME corr might be releated along rows
                elif var['inib'] == pos and var['endb'] >= pos:
                    disagr_txt = tok[:var['inic']] + corr
    
                # AB]C... #FIXME corr might be releated along rows
                elif var['inib'] <= pos and var['endb'] == pos:
                    disagr_txt = corr + tok[var['endc']+1:]

            else:
                disagr_txt = ''

            return '1', disagr_txt
    return '0', ''
    #for var in page['variants']:
    #    if var['inib'] <= pos and var['endb'] >= pos:
    #        corr = var['lay'].replace('#', ' ') if var['lay'] else ''
    #        #if var['inib'] <= pos:
    #        #    if var['endb'] >= pos:
    #        #        base = calculate_absent(pos, tok, page['lacunas'], page['illegible'], page['unclear'])
    #        #    else:
    #        #        base = calculate_absent(pos, tok, page['lacunas'], page['illegible'], page['unclear'], limit_inic=None, limit_endc=var['endc'])
    #        #else:
    #        #    if var['endb'] >= pos:
    #        #        base = calculate_absent(pos, tok, page['lacunas'], page['illegible'], page['unclear'], limit_inic=var['inic'], limit_endc=None)
    #        #    else:
    #        #        base = calculate_absent(pos, tok, page['lacunas'], page['illegible'], page['unclear'], limit_inic=None, limit_endc=var['endc'])
    #        return '1', base+corr
    #return '0', ''



if __name__ == '__main__':

    parser = ArgumentParser(description='map InterSaME manuscript text to Cairo Quran')
    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin, help='json file')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='csv file')
    parser.add_argument('--source', default='tanzil-uthmani', help='quranic source for rasm [default tanzil-uthmani]')
    parser.add_argument('--no_sign', action='store_true', help='do not add ms signature to csv output')
    parser.add_argument('--sep', default=SEP, help=f'separator [default {SEP}]')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    args = parser.parse_args()

    fragm = json.load(args.infile)

    sign, folio, side, line = '', '', '', ''

    #
    # prepare morphological analysis
    #

    morf_ref = {}
    with open(DT_QURAN_FNAME) as infp:
        dt_quran = json.load(infp)
        for item in dt_quran:

            morf_ref[(item["sura"], item["vers"], item["word"])] = {
                'POS' : ';'.join((i['POS'] for i in item['morf'])),
                'type' : ';'.join((i['type'] for i in item['morf'])),
                'afix' : ';'.join(filter(None, (i['afix'] for i in item['morf']))),
                'derv' : ';'.join(','.join(x) for x in filter(None, (i['derv'] for i in item['morf']))),
                'lema' : ';'.join(filter(None, (i['lema'] for i in item['morf']))),
                'root' : ';'.join(filter(None, (i['root'] for i in item['morf']))),
                'flec' : ';'.join(','.join(x) for x in filter(None, (i['flec'] for i in item['morf']))),
            }

    #
    # process manuscript
    #

    hist_id = fragm[0]['meta']['hist_id']
    out = [f'qindex{args.sep}{"" if args.no_sign else "sign"+args.sep}folio{args.sep}side{args.sep}line{args.sep}ms_block{args.sep}'
           f'disagr_txt{args.sep}disagr{args.sep}fasila{args.sep}khawamis{args.sep}awashir{args.sep}miaa{args.sep}ref_paleo{args.sep}'
           f'ref_ara{args.sep}POS{args.sep}type{args.sep}lemma{args.sep}root{args.sep}afix{args.sep}derv{args.sep}flec']

    for ipage, page_obj in enumerate(fragm):

        folio = page_obj['meta']['folio']
        side = page_obj['meta']['side']
        if not args.no_sign:
            sign = page_obj['meta']['signature']            
        page = page_obj['page']

        #
        # prepare reference quran
        #

        k = 0
        while not page['blocks'][k]['ind']:
            k += 1
        inii = page['blocks'][k]['ind'][0]

        k = -1
        while not page['blocks'][k]['ind']:
            k -= 1
        endi = page['blocks'][k]['ind'][-1]

        if args.debug: print(f'[[DEBUG-01]] inii={inii} endi={endi}', file=sys.stderr) #DEBUG

        ref_blocks = [(b_ar, to_isame_trans(b_pl), ':'.join(map(str, b_i))) for _, bks in
                      rasm((inii, endi), source=args.source, paleo=True, blocks=True) for b_ar, *_, b_pl, b_i in bks]
                      
        iref = 0
        qind = ''

        for i, bloc in enumerate(page['blocks']):

            line = str(calculate_line(page_obj['page']['lines'], i))
            tok = bloc['tok']

            if args.debug: print(f'[[DEBUG-02]] line={line}\n[[DEBUG-05]] tok={tok}', file=sys.stderr) #DEBUG

            tok_ms = calculate_absent(i, tok, page['lacunas'], page['illegible'], page['unclear'])

            if args.debug: print(f'[[DEBUG-03]] tok_ms={tok_ms}', file=sys.stderr) #DEBUG

            fasila = '1' if i in page['fasilas'] else '0'
            khawamis = '1' if i in page['khawamis'] else '0'
            awashir = '1' if i in page['awashir'] else '0'
            miaa = '1' if i in page['miaa'] else '0'

            disagr, disagr_txt = contains_disagr(i, tok, page)

            # replace illegible/lacuna with *
            disagr_txt = re.sub('⟦.+?⟧|⟨.+?⟩', '*', disagr_txt)

            # replace illegible/lacuna estimated sections with asterisk
            tok_ms = ESTIMATE_REGEX.sub('*', tok_ms)
            disagr_txt = ESTIMATE_REGEX.sub('*', disagr_txt)
            disagr_txt = LACUNA_ILLEGIBLE_REGEX.sub('*', disagr_txt)

            # reduce asterisk sequences to one
            tok_ms = NORM_ASTERISK_REGEX.sub('*', tok_ms)
            disagr_txt = NORM_ASTERISK_REGEX.sub('*', disagr_txt)

            if not tok_ms and tok!='∅':
                print(f'Fatal error! Empty token "{tok}" after processing at i={i}', file=sys.stderr)
                sys.exit(1)

            if not bloc['ind']:
                if args.debug: print(f'[[DEBUG-04]] <OUT>', file=sys.stderr) #DEBUG

                out.append(args.sep.join((qind, sign, folio, side, line, tok_ms, disagr_txt, disagr, fasila, khawamis, awashir, miaa)))
                
                continue

            qind = ':'.join(map(str, bloc['ind'][0]))

            if args.debug: print(f'[[DEBUG-05]] qind={qind} iref={iref}', file=sys.stderr) #DEBUG

            try:
                refbk_ara, refbk_pal, refbk_ind = ref_blocks[iref]
            except IndexError:
                print('Warning! Quran index could not be retrieved at: ', qind, sign, folio, side, line, tok_ms, disagr_txt, disagr, fasila,
                          khawamis, awashir, miaa, refbk_pal, refbk_ara, POS, typ, lema, root, afix, derv, flec, file=sys.stderr)            

            j = tuple(bloc['ind'][0][:-1])

            POS = morf_ref[j]['POS']
            typ = morf_ref[j]['type']
            afix = morf_ref[j]['afix']
            derv = morf_ref[j]['derv']
            lema = morf_ref[j]['lema']
            root = morf_ref[j]['root']
            flec = morf_ref[j]['flec']

            while refbk_ara in ('۞', '۩'):
                # this is the only row we don't fill with ms metadata as it does not contain text
                out.append(SEP.join((refbk_ind, '', '', '', '', '', '', '', '', '', '', refbk_pal, refbk_ara, POS, typ, lema, root, afix, derv, flec)))
                iref += 1
                refbk_ara, refbk_pal, refbk_ind = ref_blocks[iref]
                if args.debug: print(f'[[DEBUG-06]] <OUT>', file=sys.stderr) #DEBUG

            if qind == refbk_ind:
                out.append(args.sep.join((qind, sign, folio, side, line, tok_ms, disagr_txt, disagr, fasila, khawamis, awashir, miaa, refbk_pal, refbk_ara, POS, typ, lema, root, afix, derv, flec)))
                if args.debug: print(f'[[DEBUG-07]] <OUT>', file=sys.stderr) #DEBUG
            else:
                # 2 tok in ms -> 1 tok in ref
                # {"tok": "S,,,B,,+,,Aᵃ→ᵃ←©+ˀ↑", "ind": [[4,78,20,1]], "end": false},
                # {"tok": "Hᵘ←-ᵘ←!", "ind": [[4,78,20,1]],"end": true},
                if iref > 0 and qind == ref_blocks[iref-1][-1]:
                    iref -= 1
                    out.append(args.sep.join((qind, sign, folio, side, line, tok_ms, disagr_txt, disagr, fasila, khawamis, awashir, miaa)))
                    if args.debug: print(f'[[DEBUG-08]] <OUT>', file=sys.stderr) #DEBUG
                    
                else:
                    out.append(args.sep.join((refbk_ind, sign, folio, side, line, '', '', '', '', '', '', '', refbk_pal, refbk_ara, POS, typ, lema, root, afix, derv, flec)))
                    if args.debug: print(f'[[DEBUG-09]] <OUT>', file=sys.stderr) #DEBUG

            if len(bloc['ind'])>1:
                for _ in bloc['ind'][1:]:
                    iref += 1
                    refbk_ara, refbk_pal, refbk_ind = ref_blocks[iref]
                    out.append(args.sep.join((refbk_ind, sign, folio, side, line, '', '', '', '', '', '', '', refbk_pal, refbk_ara, POS, typ, lema, root, afix, derv, flec)))
                    if args.debug: print(f'[[DEBUG-10]] <OUT>', file=sys.stderr) #DEBUG

            iref += 1

    args.outfile.write('\n'.join(out))



