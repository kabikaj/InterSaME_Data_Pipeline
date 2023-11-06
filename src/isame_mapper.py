#!/usr/bin/env python3
#
#    isame_mapper.py
#
# map InterSaME manuscript text to Cairo Quran
#
# for checking morfo info...
#   $ cat qc_quran.json | jq -C '.[] | select(.sura==4 and .vers==143 and .word==14)' | less -R
#   $ cat qc_quran.json | jq -r .[].tok | rasm --pal
#
# exmaples:
#   $ cat testing_workflow/example_330b_3r-3v.pre.json | python isame_mapper.py > testing_workflow/example_330b_3r-3v.json
#   $ cat ../../data/arabic/trans/foo-3-trans.xml | python isame_xml2txt.py --rm_note_tags | tee  ../../data/arabic/trans/foo-4.txt |
#     python isame_parser.py | tee ../../data/arabic/trans/foo-5-pre.json | python isame_mapper.py --debug 2>&1 >/dev/null | less
#
#####################################################################################################################################

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

from argparse import ArgumentParser, FileType

from isame_util import ARCH, LINE_FILLER, EMPTY_SET, calculate_line, word_sub_variant, diff_variant, split_blocks

from rasm import rasm

RASM_STRIP_REGEX = re.compile(fr'[^{ARCH}]')

class InterSaMEMappingError(Exception):
    """ Exception for error while mapping InterSaME text.

    """
    pass

def quran_map(infp, outfp, debug=False):
    """

    Args:
        infp (io.TextIOWrapper):
        outfq (io.TextIOWrapper):
        debug (bool): show debugging info.

    Raise:
        InterSaMEMappingError

    """
    struct = json.load(infp)

    for ipage in range(len(struct)):
        
        del struct[ipage]['meta']['ini_index']

        folio = struct[ipage]['meta']['folio']
        page = struct[ipage]['page']

        range_index = (page['blocks'][0]['ind'][0], (page['blocks'][-1]['ind'][0][0]+1, None, None, None))

        ref = list((b[1], b[3], b[4]) for _, blocks in rasm(range_index, source='tanzil-uthmani', blocks=True, paleo=True) for b in blocks)

        ibloc, iref, nblocs = 0, 0, len(page['blocks'])
        prev_ind = None
        prev_btok_var = None

        while ibloc < nblocs:
            
            btok = page['blocks'][ibloc]['tok']
            ind = page['blocks'][ibloc]['ind'][0]
            sura, vers, word, bloc = ind
            
            if ref[iref][1] in '۞۩':
                iref += 1

            ref_rasm, ref_pal, ref_ind = ref[iref]
            ref_sura, ref_vers, ref_word, ref_bloc = ref_ind

            if ibloc not in page['fasilas'] and ibloc not in page['khawamis'] and \
               ibloc not in page['awashir'] and ibloc not in page['miaa'] and btok != LINE_FILLER:

                # calculate the reference if there is a variant
                btok_var, _ = diff_variant(page['variants'], btok, ibloc, logging, debug)
                btok_var_blocks = list(split_blocks(RASM_STRIP_REGEX.sub('', btok_var)))
                nbtok_var = len(btok_var_blocks)

                if RASM_STRIP_REGEX.sub('', btok) == ref_rasm:
                    if debug:
                        logging.debug(f"+YES (1) ibloc={ibloc:<4} btok={btok:<16} rasm_strip(btok)={RASM_STRIP_REGEX.sub('', btok):<10} ind={str(ind):<16} "
                                      f"ref_rasm={ref_rasm:<10} ref_pal={ref_pal:<10} ref_ind={str(ref_ind):<16}")
                    
                    page['blocks'][ibloc]['ind'] = [ref_ind]

                else:                     

                    # process case [ø/#]
                    if EMPTY_SET in btok and word_sub_variant(page['variants'], ibloc, btok.index(EMPTY_SET)):
                        page['blocks'][ibloc]['ind'] = [ref_ind, ref[iref+1][-1]]
                        if debug:
                            logging.debug(f"+YES (2) ibloc={ibloc:<4} btok={btok:<16} rasm_strip(btok)={RASM_STRIP_REGEX.sub('', btok):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} ref_pal={ref_pal:<10} ref_ind={str(ref_ind):<16}")

                    # e.g. #KLᵃ©→↕[#/∅=sub=words]MA#   rasm_strip(btok)=KL  next_btok=MA   ref_rasm=KLMA
                    elif btok != '∅' and ibloc+1<len(page['blocks']) and RASM_STRIP_REGEX.sub('', btok)+RASM_STRIP_REGEX.sub('', page['blocks'][ibloc+1]['tok']) == ref_rasm:
                        page['blocks'][ibloc]['ind'] = [ref_ind]
                        page['blocks'][ibloc+1]['ind'] = [ref_ind]
                        if debug:
                            logging.debug(f"+YES (XXX) ibloc={ibloc:<4} btok={btok:<16} rasm_strip(btok)={RASM_STRIP_REGEX.sub('', btok):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} ref_pal={ref_pal:<10} ref_ind={str(ref_ind):<16}")
                        ibloc += 1

                    # no block is splitted, e.g. [B/S=...]
                    elif RASM_STRIP_REGEX.sub('', btok_var) == ref_rasm:
                        page['blocks'][ibloc]['ind'] = [ref_ind]
                        if debug:
                            logging.debug(f"+YES (3) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")
                    
                    # e.g. #E[∅/A=r=long.vwl.noun]LBA# ; #BAᵃ←↑B[B/A=r=long.a.Y-A]BᵢBA#
                    elif RASM_STRIP_REGEX.sub('', btok_var) == ref_rasm+ref[iref+1][0]:
                        page['blocks'][ibloc]['ind'] = [ref_ind, ref[iref+1][-1]]
                        if debug:
                            logging.debug(f"+YES (4) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")
                        iref += 1

                    # e.g. #W[(A)>∅/∅=r=synt.sg.pl.dual]EᵢB{’}B{,}ᵢᵢ→#   next_btok=EᵢB’B,ᵢᵢ→   ref_rasm=EBB   btok=A   btok_var=∅A
                    elif btok=='A' and btok_var=='∅A' and RASM_STRIP_REGEX.sub('', page['blocks'][ibloc+1]['tok']) == ref_rasm:
                        page['blocks'][ibloc]['ind'] = [ref[iref-1][-1]]
                        if debug:
                            logging.debug(f"+YES (5) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")
                        iref -= 1

                    # look-ahead e.g. #S,,,B,,+,,[A/B=r=hamza]+ˀ˦H#
                    #            e.g. #R+ʷB[A/∅=r=long.vwl.noun][B,,Y⇒/Y=cd=yaat.al.idafa;r=yaat.al.idafa]#
                    elif ibloc < len(page['blocks'])-1 and RASM_STRIP_REGEX.sub('', btok_var) + \
                              RASM_STRIP_REGEX.sub('', diff_variant(page['variants'], page['blocks'][ibloc+1]['tok'], ibloc+1, logging, debug)[0]) == ref_rasm:
                        page['blocks'][ibloc]['ind'] = [ref_ind]
                        page['blocks'][ibloc+1]['ind'] = [ref_ind]
                        if debug:
                            logging.debug(f"+YES (6) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")
                        ibloc += 1

                    # look ref behind e.g. [⟨1-2r⟩>∅/∅=r=unknown]D’[⟨1-2r⟩>LKM/LKM=r=unknown]# // match LKM against ref
                    elif prev_btok_var and RASM_STRIP_REGEX.sub('', prev_btok_var).endswith(ref_rasm):
                        # add index to the previous block
                        page['blocks'][ibloc-1]['ind'].append(ref_ind)
                        # decrese ibloc to parse it again
                        if debug:
                            logging.debug(f"+YES (7) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")
                        ibloc -= 1

                    # look ref behind e.g. #A[⟨1-2r⟩>S+,,,/S=r=unknown]B’’HR’ // consider S when matching BHR
                    elif prev_btok_var and RASM_STRIP_REGEX.sub('', prev_btok_var+btok_var).endswith(ref_rasm):
                        page['blocks'][ibloc]['ind'] = [ref_ind]
                        if debug:
                            logging.debug(f"+YES (8) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")

                    # swap: e.g. D[WA/AW=r=spell.vwl.AYW]Dᵃ←+a#
                    elif RASM_STRIP_REGEX.sub('', btok) == ref[iref+1][0] and ibloc<len(page['blocks'])-1 and RASM_STRIP_REGEX.sub('', page['blocks'][ibloc+1]['tok']) == ref_rasm:                    
                        page['blocks'][ibloc]['ind'] = [ref_ind]
                        page['blocks'][ibloc+1]['ind'] = [ref[iref+1][-1]]
                        if debug:
                            logging.debug(f"+YES (9) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"next_btok={page['blocks'][ibloc+1]['tok']:<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")
                        iref += 1
                        ibloc += 1

                    # look btok behind e.g. #SBᵢ→≠![AB’’H>B’’ᵘ→©Hᵘ©/BˀᵘHᵘʷ=r=ta.marb]#
                    elif prev_btok_var and RASM_STRIP_REGEX.sub('', prev_btok_var).endswith(RASM_STRIP_REGEX.sub('', btok_var)):
                        # add same index as the one of the previous block
                        page['blocks'][ibloc]['ind'] = [ref[iref-1][-1]]
                        if debug:
                            logging.debug(f"+YES (10) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"prev_btok_var={prev_btok_var:<16} rasm_strip(prev_btok)={RASM_STRIP_REGEX.sub('', prev_btok_var):<10} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")
                        iref -= 1

                    # e.g. #RE[{MWA}>MB’’Mᵘ/MᵒB’’ᵘM=r=synt.pron]#MN#    next_btok=A   next_next_btok=MN   ref_rasm_next=MN
                    elif ibloc<len(page['blocks'])-2 and page['blocks'][ibloc+1]['tok'] == 'A' and page['blocks'][ibloc+2]['tok'] == ref[iref+1][0]:
                        page['blocks'][ibloc]['ind'] = [ref_ind]
                        page['blocks'][ibloc+1]['ind'] = [ref_ind]
                        if debug:
                            logging.debug(f"+YES (11) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"prev_btok_var={prev_btok_var:<16} rasm_strip(prev_btok)={RASM_STRIP_REGEX.sub('', prev_btok_var):<10} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")
                        ibloc += 1

                    # e.g. #BG[5-6r>BKM#  btok=BG5-6r ref_rasm=BGBKM  next_btok=A   ref_rasm_next=A
                    elif 'r' in btok and ref_rasm.startswith(RASM_STRIP_REGEX.sub('', btok)) and page['blocks'][ibloc+1]['tok'] == ref[iref+1][0]:
                        # add index to the previous block
                        page['blocks'][ibloc]['ind'] = [ref_ind]
                        if debug:
                            logging.debug(f"+YES (12) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")

                    # look-ahead e.g. #G,[Aᵢ←↑B/ᵢBˀᵒ=r=hamza]B’’ᵢ!+i#
                    elif ibloc < len(page['blocks'])-1 and RASM_STRIP_REGEX.sub('', btok).endswith('A') and \
                                    RASM_STRIP_REGEX.sub('', btok)[:-1] + RASM_STRIP_REGEX.sub('', page['blocks'][ibloc+1]['tok']) == ref_rasm and \
                                    ref_rasm.startswith(RASM_STRIP_REGEX.sub('', btok_var)):
                        page['blocks'][ibloc]['ind'] = [ref_ind]
                        page['blocks'][ibloc+1]['ind'] = [ref_ind]
                        if debug:
                            logging.debug(f"+YES (13) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")
                        ibloc += 1

                    # look-ahead next page e.g. btok=LFA  #ALF[A/∅ᵃᴬ=r=spell.vwl.AYW] ... (=S)FWNᵃ#   M="LFA SFW"  vs  CQ="LFSFW N" 
                    # look-behind previous page
                    elif ibloc == len(page['blocks'])-1 and ipage < len(struct) and \
                                    RASM_STRIP_REGEX.sub('', btok).endswith('A') and \
                                    RASM_STRIP_REGEX.sub('', btok)[:-1] + RASM_STRIP_REGEX.sub('', struct[ipage+1]['page']['blocks'][0]['tok']) == ref_rasm:
                        page['blocks'][ibloc]['ind'] = [ref_ind]
                        if debug:
                            logging.debug(f"+YES (14) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")
                        ibloc += 1

                    elif ibloc == 0 and ipage > 0 and \
                                    RASM_STRIP_REGEX.sub('', struct[ipage-1]['page']['blocks'][-1]['tok']).endswith('A') and \
                                    RASM_STRIP_REGEX.sub('', struct[ipage-1]['page']['blocks'][-1]['tok'])[:-1] + RASM_STRIP_REGEX.sub('', btok) == ref_rasm:
                        page['blocks'][ibloc]['ind'] = [ref_ind]
                        if debug:
                            logging.debug(f"+YES (14) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} ref_ind=({str(ref_ind):<16}, {str(ref[iref+1][-1]):<16})")

                    # check for multiple blocks [∅>WAᵃ©→↑M⟨BEB⟩ᵢ⟨KM⟩/WᵃAˀᵃMᵒB’’ᵢEᵃB’’ᵢKᵘMᵒ=r=mech.haplog]
                    elif btok_var_blocks == [ref[i][0] for i in range(iref, iref+nbtok_var)]:
                        ref_ind_next_list = [ref[i][-1] for i in range(iref, iref+nbtok_var)]
                        page['blocks'][ibloc]['ind'] = [ref_ind] + ref_ind_next_list
                        if debug:
                            logging.debug(f"+YES (15) ibloc={ibloc:<4} btok={btok:<16} btok_var={btok_var:<16} rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10} ind={str(ind):<16} "
                                          f"ref_rasm={ref_rasm:<10} | ref_rasm_next={ref[iref+1][0]:<10} ref_pal={ref_pal:<10} "
                                          f"btok_var_blocks={btok_var_blocks}  ref_blocks={[ref[i][0] for i in range(iref, iref+nbtok_var)]} "
                                          f"ref_ind_next_list={ref_ind_next_list}")
                        iref += nbtok_var-1

                    else:
                        if debug:
                            nextbloc = page['blocks'][ibloc+1]['tok'] if ibloc < len(page['blocks'])-1 else '?'
                            nextnextbloc = page['blocks'][ibloc+2]['tok'] if ibloc < len(page['blocks'])-2 else '?'
                            logging.debug(f"- NO!! ibloc={ibloc:<4} btok={btok:<16} rasm_strip(btok)={RASM_STRIP_REGEX.sub('', btok):<10}\n                "
                                          f"             {' '*33} btok_var={btok_var:<16}  rasm_strip(btok_var)={RASM_STRIP_REGEX.sub('', btok_var):<10}\n                "
                                          f"             {' '*33} ind={str(ind):<16}\n"
                                          f"             {' '*43} ref_rasm={ref_rasm} (next={ref[iref+1][0]}) ref_pal={ref_pal:<10} ref_ind={str(ref_ind):<16}\n"
                                          f"             {' '*43} prev_btok_var={prev_btok_var}\n"
                                          f"             {' '*43} || next_btok={nextbloc:<16} next_next_btok={nextnextbloc:<16} ref_rasm_next={ref[iref+1][0]:<10}")

                        line = re.sub(r'\.0$', '', str(calculate_line(page['lines'], ibloc)))
    
                        logging.debug(f"Fatal error! inconsistent mapping against reference Quran in [[{folio}.L{line}]] bloc={btok}")

                        raise InterSaMEMappingError

                prev_btok_var = btok_var
                iref += 1

            # dividers should not have an index
            else:
                page['blocks'][ibloc]['ind'] = []
                if debug:
                    logging.debug(f" DIV ibloc={ibloc:<4} btok={btok:<16}")

            ibloc += 1
            prev_ind = ref_ind

    json.dump(struct, outfp, ensure_ascii=False, indent=4)

if __name__ == '__main__':

    parser = ArgumentParser(description='map InterSaME manuscript text to Cairo Quran')
    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin, help='json file')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='enriched json file')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    args = parser.parse_args()

    try:
        quran_map(args.infile, args.outfile, args.debug)
    except InterSaMEMappingError:
        logging.debug("Mapping stopped!")
        sys.exit(1)
