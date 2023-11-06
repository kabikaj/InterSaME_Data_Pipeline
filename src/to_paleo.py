#!/usr/bin/env python3
#
#    to_paleo.py
#
# convert Arabic script o Latin paleographic representation
#
# Taken from the rasm-arch library: https://pypi.org/project/rasm-arch/
#
# usage:
#   $ cat ../../data/arabic/transcriptions/F002_Q.23.80-46.25_frgm_14ff.txt | python to_paleo.py --rm_cons_strokes
#     > ../../data/arabic/transcriptions/F002_Q.23.80-46.25_frgm_14ff_converted.txt
#
################################################################################################

import re
import sys
from argparse import ArgumentParser, FileType

STROKE_ABOVE = '’'
STROKE_BELOW = ','

MAPPING_RASM = {
    'Q' : 'ٯ' ,
    'N' : 'ں' ,
    'Y' : 'ي' ,  ##### ARABIC YA
    'B' : 'ٮ' ,
    'G' : 'ح' ,
    'T' : 'ط' ,
    'C' : 'ص' ,
    'S' : 'س' ,
    'F' : 'ڡ' ,
    'E' : 'ع' ,
    'H' : 'ه' ,
    'M' : 'م' ,
    'L' : 'ل' ,
    'K' : 'ک' ,
    'A' : 'ا' ,
    'R' : 'ر' ,
    'D' : 'د' ,
    'W' : 'و' ,
}

ARCHIGRAPHEMES = ''.join(MAPPING_RASM.keys())

MAPPING_TRANS = {
    'أ' : 'Aˀ˥' ,
    'ؤ' : 'Wˀ˥' ,
    'إ' : 'Aˀ˩' ,
    'ء' : 'ʔ' ,
    'ٱ' : 'Aᵟ' ,
    'آ' : 'A˜' ,
    'ا' : 'A' ,
    'ب' : 'B' ,
    'ت' : 'B' ,
    'ث' : 'B' ,
    'ج' : 'G' ,
    'ح' : 'G' ,
    'خ' : 'G' ,
    'د' : 'D' ,
    'ذ' : 'D' ,
    'ر' : 'R' ,
    'ز' : 'R' ,
    'س' : 'S' ,
    'ش' : 'S' ,
    'ص' : 'C' ,
    'ض' : 'C' ,
    'ط' : 'T' ,
    'ظ' : 'T' ,
    'ع' : 'E' ,
    'غ' : 'E' ,
    'ف' : 'F' ,
    'ك' : 'K' ,
    'ل' : 'L' ,
    'م' : 'M' ,
    'ه' : 'H' ,
    'ة' : 'H' ,
    'و' : 'W' ,
    'َ' : 'ᵃ'  ,  # fatha
    'ً' : 'ᵃⁿ' ,  # fathatan
    'ࣰ' : 'ᵃᵐ' ,  # open fathatan
    'ُ' : 'ᵘ'  ,  # damma
    'ٌ' : 'ᵘⁿ' ,   # dammatan
    'ࣱ' : 'ᵘᵐ' , # open dammatan
    'ِ' : 'ᵢ'  ,  # kasra
    'ٍ' : 'ᵢₙ' ,  # kasratan
    'ࣲ' : 'ᵢₘ' ,  # open kasratan
    'ّ' : 'ᵚ'  ,  # sadda
    'ۡ' : 'ᵒ'  ,  # quranic sukun
    'ٓ' : '˜'  ,  # madda
    'ۨ' : 'ⁿ'  ,  # minuature nun above
    'ٰ' : 'ᴬ'  ,  # dagger alif
    'ۜ' : 'ˢ'  ,  # miniature sin above
    'ۣ' : 'ₛ'  ,  # miniature sin below
    'ۢ' : 'ᵐ'  ,  # minuature mim above
    'ۭ' : 'ₘ' ,  # # minuature mim below
    'ۥ' : 'ʷ'  ,  # minuature waw
    'ۦ' : 'ʸ'  ,  # miniature ya
    'ۧ' : 'ʸ'  ,  # minuature ya above
    '۟' : '°'  ,  # U+06df ARABIC SMALL HIGH ROUNDED ZERO - small circle | U+00B0 DEGREE SIGN
                  #   the letter is additional and should not be pronounced either in connection nor pause
    '۠' : '⁰'  ,  # U+06e0 ARABIC SMALL HIGH UPRIGHT RECTANGULAR ZERO - oval sign
                  #   above an alif followed by a vowel letter, indicates that it is additional in consecutive reading
                  #   but should be pronounced in pause
    '۫' : '⌃'  ,  # U+06eb ARABIC EMPTY CENTRE HIGH STOP | U+2303 (alt-08963)  UP ARROWHEAD ; hapax تَأۡمَ۫نَّا
    '۪' : '⌄'  ,  # U+06ea ARABIC EMPTY CENTRE LOW STOP | U+2304 DOWN ARROWHEAD ; hapax مَجۡر۪ىٰهَا
    '۬' : '•'  ,  # U+06ec ARABIC ROUNDED HIGH STOP WITH FILLED CENTRE | U+2022 BULLET ; hapax ءَا۬عۡجَمِىࣱّ
    'ٔ' : 'ˀ˥' ,  # hamza above
    'ٕ' : 'ˀ˩'  ,  # hamza below
    'ـٔ ' : 'ˀ˥' ,  # U+0640 "ـ" tatweel is ALWAYS followed by hamza above, eg. ٱلۡأَفۡـِٔدَةِ 104:7:4,601:49,821:8:4
    # pausal marks
    'ۖ' : '⒮',  # U+06d6 ARABIC SMALL HIGH LIGATURE SAD WITH LAM WITH ALEF MAKSURA
    'ۗ' : '⒬',  # U+06d7 ARABIC SMALL HIGH LIGATURE QAF WITH LAM WITH ALEF MAKSURA
    'ۘ' : '⒨',  # U+06d8 ARABIC SMALL HIGH MEEM INITIAL FORM
    'ۙ' : '⒧',  # U+06d9 ARABIC SMALL HIGH LAM ALEF
    'ۚ' : '⒥',  # U+06da ARABIC SMALL HIGH JEEM
    'ۛ' : '∴',   # U+06db ARABIC SMALL HIGH THREE DOTS
}


REGEX_TRANS = re.compile('|'.join(MAPPING_TRANS))

def to_paleo(tok, space='#', rm_cons_strokes=False, sep_non_join=False, debug=False):
    """ Convert all Arabic-scriped text within string tok into paleographic transcription.
    Keep the rest untouched.

    Args:
        tok (str): text.
        space (string): character used for indicating space.
        rm_cons_strokes (bool): If True, remove consonantal strokes in conversion.
        sep_non_join (bool): Separate non joinin letters by a space
        debug (bool): show debugging info.

    Return:
        str: modified text.

    """
    if debug: print(f'@DEBUG[1]@ {tok}', file=sys.stderr) #TRACE

    # convert strokes
    tok = re.sub(r'([بج])', rf'\1{STROKE_BELOW}', tok)
    if debug: print(f'@DEBUG[2]@ {tok}', file=sys.stderr) #TRACE
    tok = re.sub(r'([خذزنضظغف])', rf'\1{STROKE_ABOVE}', tok)
    if debug: print(f'@DEBUG[3]@ {tok}', file=sys.stderr) #TRACE
    tok = re.sub(r'([ةتق])', rf'\1{STROKE_ABOVE}{STROKE_ABOVE}', tok)
    if debug: print(f'@DEBUG[4]@ {tok}', file=sys.stderr) #TRACE
    tok = re.sub(r'([ثش])', rf'\1{STROKE_ABOVE}{STROKE_ABOVE}{STROKE_ABOVE}', tok)
    if debug: print(f'@DEBUG[5]@ {tok}', file=sys.stderr) #TRACE

    # convert simple mapping
    tok = REGEX_TRANS.sub(lambda m: MAPPING_TRANS[m.group(0)], tok)
    if debug: print(f'@DEBUG[6]@ {tok}', file=sys.stderr) #TRACE
    
    # convert special archigraphemes - NQY
    tok = tok.replace('ئ', 'ىˀ˥')
    if debug: print(f'@DEBUG[7]@ {tok}', file=sys.stderr) #TRACE
    tok = re.sub(rf'ن([^{ARCHIGRAPHEMES}نىيق]*(?: |$))', r'N\1', tok)
    if debug: print(f'@DEBUG[8]@ {tok}', file=sys.stderr) #TRACE
    tok = re.sub(rf'[ىي]([^{ARCHIGRAPHEMES}ىيق]*(?: |$))', r'Y\1', tok)
    if debug: print(f'@DEBUG[9]@ {tok}', file=sys.stderr) #TRACE

    tok = re.sub(rf'[نىي]', r'B', tok)
    if debug: print(f'@DEBUG[A]@ {tok}', file=sys.stderr) #TRACE
    tok = re.sub(rf'ق([^{ARCHIGRAPHEMES}ق]*(?: |$))', r'Q\1', tok)
    tok = tok.replace('ق', 'F')
    if debug: print(f'@DEBUG[B]@ {tok}', file=sys.stderr) #TRACE

    # separate letterblocks - ARDW
    if sep_non_join:
        tok = re.sub(rf'([ARDW][^{ARCHIGRAPHEMES}]*)', rf'\1{space}', tok).strip()

    # change only the spaces found within texts (InterSame transcription)
    tok = re.sub(r' (?! )', fr'{space}', tok)

    if rm_cons_strokes:
        tok = re.sub(rf'[{STROKE_ABOVE}{STROKE_BELOW}]', '', tok)

    # revert order of diacritics with alif so that all follow the alif
    tok = re.sub(r'([~ʔʷˀ˥ـᴬᵃᵐᵒᵘᵚᵢⁿ]+)A', r'A\1', tok)

    # remove tatweel
    return tok.replace('ـ', '')


if __name__ == '__main__':

    parser = ArgumentParser(description='convert Arabic script o Latin paleographic representation')
    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin, help='input file')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='output file')
    parser.add_argument('--rm_cons_strokes', action='store_true', help='ignore consonantal strokes in the conversion')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    args = parser.parse_args()

    for line in (l.strip() for l in args.infile):
        if line.startswith('TITLE'):
            print(line, file=args.outfile)
        else:
            print(to_paleo(line, rm_cons_strokes=args.rm_cons_strokes, debug=args.debug), file=args.outfile)



