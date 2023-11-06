#!/ur/bin/end python3
#
#    lat2ar.py
#
# convert DOTS Latin transliteration into Arabic
#
# example:
#   $ cat ../data/initial/7_MS_latin.doc | antiword - | python lat2ar.py
#
########################################################################

import re
import sys
from bs4 import BeautifulSoup
from collections import OrderedDict
from argparse import ArgumentParser, FileType

_translation = [  
    ('='   , '='), # added so that the checking does not fail
    ('♯'   , ' '),

    ('A'   , 'ا'),
    ('Bˊˊˊ', 'ث'), # 062b
    ('Bˊˊ' , 'ت'), # 062a
    ('Bˏˏ' , 'ي'), # 064a
    #('y'   , 'ي'), # 064a #FIXME
    ('Bˏ'  , 'ب'), # 0628
    ('Bˊ'   , 'ن'), # 0646 #FIXME check only medial
    ('B'   , 'ٮ'), # 066e
    
    ('Nˊ'  , 'ن'), # 0646 #FIXME check is only final
    #('n'   , 'ن'), # 0646 #FIXME
    ('N'   , 'ں'), # 06ba #FIXME check is only final
    ('Y↓'  , 'ے'), #FIXME 
    ('Y→'  , 'ے'), #FIXME
    ('Y'   , 'ى'), # 06cc

    ('Gˊ'  , 'خ'), # 062e
    ('Gˏ'  , 'ج'), # 062c
    ('G'   , 'ح'), # 062d
    ('Dˊ'   , 'ذ'), # 0630
    ('D'    , 'د'), # 062f
    ('Rˊ'   , 'ز'), # 0632
    ('R'    , 'ر'), # 0631
    ('Sˊˊˊ' , 'ش'), # 0634
    ('Sˏˏˏ' , 'ڜ'), #FIXME
    ('S'    , 'س'), # 0633
    ('Cˊ'   , 'ض'), # 0636
    ('C'    , 'ص'), # 0635
    ('Tˊ'   , 'ظ'), # 0638
    ('T'    , 'ط'), # 0637
    ('Eˊ'   , 'غ'), # 063a
    ('E'    , 'ع'), # 0639
    
    ('Fˊˊ' , 'ق'), # 0642
    #('q'   , 'ق'), # 0642 #FIXME
    ('Fˊ'  , 'ف'), # 0641
    #('f'   , 'ف'), # 0641 #FIXME
    ('Fˏ'  , 'ڢ'), # 06a2
    ('F'   , 'ڡ'), # 06a1
    ('Qˊ'  , 'ڧ'), # 06a7 #FIXME check this only occur as final
    ('Q'   , 'ٯ'), # 066f #FIXME check this only occur as final

    ('K' , 'ك'), # 06a9
    ('L' , 'ل'), # 0644
    #('l' , 'ل'), # 0644 #FIXME
    ('M' , 'م'), # 0645
    ('H' , 'ه'), # 0647
    #('h' , 'ه'), # 0647 #FIXME
    ('W' , 'و'), # 0648

    ('˚' , 'َ'), # 0618
    ('·' , 'ُ'), # 064f
    ('˳' , 'ِ'), # 061a
    ('˸' , 'ً'), #FIXME
    (':' , 'ٌ'), #FIXME
    ('꜈', 'َ'), # a708 > ??
    ('꜉', 'َ'), # a709 > ??
    ('꜊', 'ُ'), # a70a > ??
    ('꜋', 'ِ'), # a70b > ??
    ('꜌', 'ِ'), # a70c > ??
    ('꜍', 'َ'), # a70d > ??
    ('꜎', 'َ'), # a70e > ??
    ('꜏', 'ُ'), # a70f > ??
    ('꜐', 'ِ'), # a710 > ??
    ('꜑', 'ِ'), # a711 > ??
    ('ᵃ', 'ٰ'), # 0670
    ('ᵘ', 'ۥ'), # 06e5 
    ('˅' , 'ء'), #FIXME
]

mapping = OrderedDict(_translation)

rules = [
    (r'&fāṣila;([0-9]..._[0-9])?', '<fasila>'),  #FIXME do not use capital letters here !!! and add checking
    (r'<[0-9]+>',      '<sura>'),
    *_translation,
    ('.', 'UNK')
]

TRANSLIT_REGEX = re.compile('|'.join(mapping))



def lat2ar(lines):
    """ convert DOTS latin transliteration into Arabic

    Args:
        lines (list): lines of text to convert.

    Return: #FIXME
        list: lines of result text in Arabic. #FIXME

    """
    #
    # check errors
    #

    unknown = list(char for char,known in
             ((ch, ch in mapping.keys()) for ch in set(c for l in lines for c in l)) if not known)
    
    if unknown:
        for char in unknown:
            print(f'Error! character \'{char}\' unknown', file=sys.stderr)
    
    scanner = re.Scanner(rules)
        
    for i, line in enumerate(lines, 1):

        conversion, _ = scanner.scan(line)

        if 'UNK' in conversion:
            print(f'\nError in line {i} "{line}"', file=sys.stderr)
            print(f'Unknown character(s): {conversion}', file=sys.stderr)

    #
    # apply conversion
    #

    newlines = (TRANSLIT_REGEX.sub(lambda m: mapping[m.group(0)], line) for line in lines)
    
    yield from newlines

if __name__ == '__main__':

    parser = ArgumentParser(description='convert DOTS Latin transliteration into Arabic')
    parser.add_argument('input', nargs='?', type=FileType('r'), default=sys.stdin, help='text file in Latin transliteration')
    parser.add_argument('output', nargs='?', type=FileType('w'), default=sys.stdout, help='output text file for dumping Arabic conversion')
    args = parser.parse_args()

    lines = list(filter(None, ((l.strip() for l in args.input.readlines()))))

    print('\n'.join(lat2ar(lines)), file=args.output)

