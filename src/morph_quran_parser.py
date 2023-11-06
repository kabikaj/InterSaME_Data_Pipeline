#!/usr/env python3
#
#    morph_quran_parser.py
#
# parse the morph annotation of the quran from the university of haifa
#
# usage:
#   $ cat ../data/arabic/morph_tagging_quran/qorout.txt | python morph_quran_parser.py
#
######################################################################################


import sys
import ujson as json
from argparse import ArgumentParser, FileType


if __name__ == '__main__':

    parser = ArgumentParser(description='parse the morph annotation of the quran from the university of haifa')
    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin, help='source haifa file')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='output file')
    args = parser.parse_args()

    tokens = args.infile.read().split('\n\n')

    for token in tokens:
        #print(40*'-') #TRACE
        fsttok, *rest = token.split('\n')

        # one analysis
        if not rest:
            print('[1]', fsttok, rest) #TRACE

        # two analyses
        elif len(rest) == 1:
            print('[2]', fsttok, rest) #TRACE

        # three analyses
        elif len(rest) == 2:
            print('[3]', fsttok, rest) #TRACE

        # four analyses
        elif len(rest) == 3:
            print('[4]', fsttok, rest) #TRACE

        # five analyses
        elif len(rest) == 4:
            print('[5]', fsttok, rest) #TRACE

        # six analyses
        elif len(rest) == 5:
            print('[6]', fsttok, rest) #TRACE

        # eight analyses
        elif len(rest) == 7:
            print('[8]', fsttok, rest) #TRACE

        # ten analyses
        elif len(rest) == 9:
            print('[A]', fsttok, rest) #TRACE

        # sixteen analyses
        elif len(rest) == 15:
            print('[0]', fsttok, rest) #TRACE

        # other amount of analyses
        else:
            print('[other]', fsttok, rest) #TRACE
            


#li-llaah-i  l+Prep+Def+llaah+ProperName+Gen
#
#rabb-i  rbb+fa&l+Noun+Triptotic+Masc+Sg+Pron+Dependent+1P+Sg
#rabb-i  rbb+fa&l+Noun+Triptotic+Masc+Sg+Gen
#
#l-&aalam-iina   Def+&lm+faa&al+Noun+Triptotic+Masc+Pl+Obliquus
