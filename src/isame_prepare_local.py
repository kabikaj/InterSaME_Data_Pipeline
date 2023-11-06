#!/usr/bin/env python3
#
#    isame_prepare.py
#
# convert Arabic script to Latin paleographic representation and created two template files for working in Archetype:
# one in Latin in Arabic.
#
# Notice that in the Arabic draft, we use U+200c ZERO WIDTH NON-JOINER so that the mark for the line (e.g., |‌1‌ ‌|)
# is not separated with the justification. 
#
# example:
#   $ cat ../../data/arabic/trans/F014_BnF.Ar.338c-1-ini.txt | python isame_prepare.py --ya_tail_marks --G_tail_marks
#     --out_pal ../../data/arabic/trans/F014_BnF.Ar.338c-2-draft-pl.txt --out_ara ../../data/arabic/trans/F014_BnF.Ar.338c-2-draft-ar.txt
#
#########################################################################################################################################

import io
import re
import sys
from argparse import ArgumentParser, FileType

from isame_util import CUSTOM_MAPPING, VOWELS

from rasm import rasm

# rasm uses a different way to encode diacritic dots
# noramise it to InterSaME
STROKES = {'¹': '’',
           '²': '’’',
           '³': '’’’',
           '₁': ',',
           '₂': ',,',
           '₃': ',,,'}       

STROKES_REGEX = re.compile('|'.join(STROKES))

def prepare_custom(rm_cons_stokes=False,
                   rm_vowels=False,
                   rm_cons_final_ya=False,
                   rm_cons_fa_qaf=False,
                   qaf_below=False,
                   qaf_above=False,
                   fa_below=False,
                   dotted_ta_marbuta=False,
                   ya_tail_marks=False,
                   G_tail_marks=False):
    """ Prepare regex to customise transcription of paleo-orthpgraphic representation.

    Args:
        rm_cons_strokes (bool): do not mark any archihrapheme with strokes.
        rm_vowles (bool):
        rm_cons_final_ya (bool): remove consonantal diacritics for final ya
        qaf_above (bool): mark qaf with a stroke below instead of with the standard two strokes above.
        qaf_below (bool): 
        fa_below (bool): mark qaf with one dot above and fa with one dot below.
        dotted_ta_marbuta (bool): do not mark ta marbuta with strokes.
        ya_tail_marks (bool): Add tail marks to ya (Y⇒⇓).
        G_tail_marks (bool): Add tail marks to G (G⇐⇘).

    Return:
        str: modified string.

    """
    if qaf_below and qaf_above:
        print('Fatal error! both "qaf_above" and "qaf_below" stroke indicated!', file=sys.stderr)
        print('Preparation aborted!', file=sys.stderr)
    if qaf_below and fa_below:
        print('Fatal error! both "qaf_below" and "fa_below" stroke indicated!', file=sys.stderr)
        print('Preparation aborted!', file=sys.stderr)

    if rm_vowels:
        for v in VOWELS:
            CUSTOM_MAPPING[v] = ''

    if rm_cons_final_ya:
        CUSTOM_MAPPING['Y,,'] = 'Y'

    if rm_cons_stokes:
        CUSTOM_MAPPING['’'] = ''
        CUSTOM_MAPPING[','] = ''
    else:
        if rm_cons_fa_qaf:
            CUSTOM_MAPPING['F’’'] = 'F'
            CUSTOM_MAPPING['F’'] = 'F'
            CUSTOM_MAPPING['Q’’'] = 'Q'
        else:
            if qaf_above:
                CUSTOM_MAPPING['F’’'] = 'F’'
                CUSTOM_MAPPING['Q’’'] = 'Q’'
            if qaf_below:
                CUSTOM_MAPPING['F’’'] = 'F,'
                CUSTOM_MAPPING['Q’’'] = 'Q,'
            if fa_below:
                CUSTOM_MAPPING['F’'] = 'F,'

        if not dotted_ta_marbuta:
            CUSTOM_MAPPING['H’’'] = 'H'
    
    if ya_tail_marks:
        CUSTOM_MAPPING['Y'] = 'Y⇒⇓'
    if G_tail_marks:
        CUSTOM_MAPPING['G'] = 'G⇐⇘'


    return re.compile('|'.join((r'G(?=[^A-Z]*(#|$))' if k=='G' else r'F’(?!’s)' if k=='F’' else k) for k in CUSTOM_MAPPING))

def convert2lat(line):
    """ convert line to Latin Paleographic representation keeping i:j references, equals = and hyphens - 
        so that we don't loose them in the rasm conversion.

    Args:
        line (str): line to convert.

    Yield:
        modified line.

    """
    for chunk in filter(lambda x: x.strip(), re.split(r'(=|[0-9]+:[0-9]+|\-)', line.strip())):
        if chunk[0] in '123456789=-…':
            yield chunk
        else:
            yield custom_regex.sub(lambda m: CUSTOM_MAPPING[m.group(0)], '#'.join(t[-1].replace(' ', '')
                for t in rasm(io.StringIO(chunk), paleo=True)))

if __name__ == '__main__':

    parser = ArgumentParser(description='convert Arabic script o Latin paleographic representation')
    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin, help='input file')
    parser.add_argument('--out_pal', required=True, type=FileType('w'), help='output file for paleography conversion')
    parser.add_argument('--out_ara', required=True, type=FileType('w'), help='output file for Arabic version')
    parser.add_argument('--rm_cons_stokes', action='store_true', help='do not mark any archihrapheme with strokes')
    parser.add_argument('--rm_vowels', action='store_true', help=f'do not show vowels ({", ".join(VOWELS)})')
    parser.add_argument('--rm_cons_final_ya', action='store_true', help=f'remove consonantal diacritics for final ya')

    parser.add_argument('--rm_cons_fa_qaf', action='store_true', help=f'remove consonantal diacritics of fa and qaf')

    qaf_strokes = parser.add_mutually_exclusive_group()
    qaf_strokes.add_argument('--qaf_below', action='store_true', help='mark qaf with one stroke below')
    qaf_strokes.add_argument('--qaf_above', action='store_true', help='mark qaf with one stroke above')
    parser.add_argument('--fa_below', action='store_true', help='mark fa with one stroke below')
    parser.add_argument('--dotted_ta_marbuta', action='store_true', help='add strokes to ta marbuta')
    parser.add_argument('--ya_tail_marks', action='store_true', help='add tail marks for ya (Y⇒⇓)')
    parser.add_argument('--G_tail_marks', action='store_true', help='add tail marks for G (G⇐⇘)')
    parser.add_argument('--not_folio_mark', action='store_true', help='do not print the folio mark between pages for archetype')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    args = parser.parse_args()


    custom_regex = prepare_custom(rm_cons_stokes=args.rm_cons_stokes,
                                  rm_vowels=args.rm_vowels,
                                  rm_cons_final_ya=args.rm_cons_final_ya,
                                  rm_cons_fa_qaf=args.rm_cons_fa_qaf,
                                  qaf_below=args.qaf_below,
                                  qaf_above=args.qaf_above,
                                  fa_below=args.fa_below,
                                  dotted_ta_marbuta=args.dotted_ta_marbuta,
                                  ya_tail_marks=args.ya_tail_marks,
                                  G_tail_marks=args.G_tail_marks)

    processed = []
    for line in (l.strip() for l in args.infile):

        # keep empty lines
        if not line:
            processed.append((None, line))

        # skip comments
        elif line[0]=='#':
            continue

        elif line.startswith('TITLE'):
            processed.append((None, line))

        elif line.startswith('Source'):
            processed.append((None, line))

        elif line.startswith('Q.'):
            processed.append((None, line))

        elif line[0] in '123456789':

            try:
                n, line = line.split('.', 1)
            except ValueError:
                print(f'Error in line "{line}"', file=sys.stderr)
                sys.exit(1)
            n = int(n)

            line_pal = '#'.join(convert2lat(line)).replace('=#', '=')
            processed.append((n, (line, line_pal)))

        # line starts with Arabic script (supplied text)
        elif ord(line[0]) >= ord('ء') and ord(line[0]) <= ord('ࣲ') or line[0]=='=':

            line_pal = '#'.join(convert2lat(line)).replace('=#', '=')
            processed.append((-1, (line, line_pal)))

        # not part of transcription nor metadata
        else:
            processed.append((None, line))
            print(f'Warning! Unexpected line: "{line}"', file=sys.stderr) #TRACE


    # add # at the end of lines if th word is not broken between the next line
    size_proc = len(processed)

    for i in range(size_proc):
        n, line = processed[i]

        if not args.not_folio_mark and n == None and line.startswith('TITLE'):
            print(f'{line.rsplit("_", 2)[-2]}\n', file=args.out_pal)
            print(f'{line.rsplit("_", 2)[-2]}\n', file=args.out_ara)

        if not n:
            print(line, file=args.out_pal)

            # for arabic, skip non text sections; keep only blank lines
            if not line:
                print(line, file=args.out_ara)

        else:
            line_ara = line[0]
            line_pal = line[1]

            if i == size_proc-1:
                line_pal += '#'

            if i < size_proc-1:
                if processed[i+1][0]:
                    if not processed[i+1][1][1].startswith('='):
                        line_pal += '#'
                else:
                    line_pal += '#'

            if n != -1:
                line_pal = f'|{n:>2}| {line_pal}'

                if n < 10:
                    line_ara = f'|‌{n}‌ ‌| {line_ara.strip()}'
                else:
                    line_ara = f'‏‏|‌{n}‌| {line_ara.strip()}'

            #line_pal = STROKES_REGEX.sub(lambda m: STROKES[m.group(0)], line_pal)
            
            print(line_pal, file=args.out_pal)
            print(line_ara.replace('=', ''), file=args.out_ara)
