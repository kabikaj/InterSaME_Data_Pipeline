#!/usr/bin/env python3
#
#    isame_get_text.py
#
# gets Quranic text from index range
#
# example:
#   $ python isame_get_text.py -i 4:95:17-4:105:9 | xclip -selection clipboard  # F014_BnF.Ar.338c
#
##################################################################################################

import re
import sys
from itertools import groupby
from argparse import ArgumentParser, FileType, ArgumentTypeError

from rasm import rasm

def parse_index_range(arg):
    """ Check if arg's format is correct, i.e., i:j:k-n:p:q
        
    Args:
        arg (startr): quranic index range.

    Return:
        ((int, int, int, int), (int, int, int, int)): ini sura, ini verse, ini word, ini block.

    Raise:
        ArgumentTypeError: if arg does not follow the expected format.

    """
    if (m := re.match(r'^(\d+):(\d+):(\d+)-(\d+):(\d+):(\d+)$', arg)):
        i,j,k, n,p,q = list(map(int, m.groups()))
        return ((i, j, k, None), (n, p, q, None))

    raise ArgumentTypeError('arg must be a complete quranic range index, e.g. 2:31:2-2:134:4')

if __name__ == '__main__':

    parser = ArgumentParser(description='gets Quranic text from index range')
    parser.add_argument('--index', '-i', type=parse_index_range, help='index range')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='output file')
    args = parser.parse_args()

    try:
        verses = groupby(((w, i) for w, *_, i in rasm(args.index, source='tanzil-uthmani')), key=lambda x: (x[1][0], x[1][1]))
        for index, verse in verses:
            print(' '.join(w for w, _ in verse), f'{index[0]}:{index[1]} ', end='', file=args.outfile)

    except (BrokenPipeError, IOError):
        pass

    sys.stderr.close()

