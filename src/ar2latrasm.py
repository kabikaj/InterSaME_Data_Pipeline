#!/ur/bin/end python3
#
#    ar2latrasm.py
#
# convert arabic text to latin rasm
#
# example:
#   $ cat ../data/arabic/decotype_quran.txt | python ar2latrasm.py > ../data/arabic/decotype_quran_latrasm.txt
#   $ echo "في سَبِيلِ فِيهِي فِي حَدِيثࣰا 4:88 ۞ فَمَا" | python ar2latrasm.py --debug
#
##############################################################################################################

import re
import sys
from argparse import ArgumentParser, FileType


MAPPING = {
    ' ' : '♯' ,
    'ا' : 'A' ,
    'ٱ' : 'A' ,
    'إ' : 'A' ,
    'أ' : 'A' ,
    'ب' : 'B' ,
    'ت' : 'B' ,
    'ث' : 'B' ,
    'ي' : 'Y' ,
    'ى' : 'Y' ,
    'ئ' : 'Y' ,
    'ن' : 'N' ,
    'خ' : 'G' , 
    'ج' : 'G' , 
    'ح' : 'G' , 
    'ذ' : 'D' ,
    'د' : 'D' ,
    'ر' : 'R' ,
    'ز' : 'R' ,
    'ش' : 'S' ,
    'س' : 'S' ,
    'ض' : 'C' ,
    'ص' : 'C' ,
    'ظ' : 'T' ,
    'ط' : 'T' ,
    'ع' : 'E' ,
    'غ' : 'E' ,
    'ف' : 'F' ,
    'ق' : 'Q' ,
    'ك' : 'K' , 
    'ل' : 'L' ,
    'م' : 'M' ,
    'ه' : 'H' ,
    'ة' : 'H' ,
    'و' : 'W' ,
    'ؤ' : 'W' ,
}

BASE = ''.join(MAPPING.keys())

REGEX = re.compile('|'.join(MAPPING))

def ar2latrasm(text, debug=False):
    """ convert Arabic text into Latin rasm.

    Args:
        text (str): input Arabic text.
        debug (bool): debug mode.

    Return:
        str: rasm conversion.

    """
    if debug: print(f'@debug::ori->{text}', file=sys.stderr) #DEBUG

    text = re.sub(f'[^{BASE}0-9:]', '', text)
    if debug: print(f'@debug::base->{text}', file=sys.stderr) #DEBUG
    
    text = re.sub(r' +', ' ', text)
    if debug: print(f'@debug::base_sp->{text}', file=sys.stderr) #DEBUG
    
    text = re.sub(r'[نيىئ](?! |$)', 'B', text)
    if debug: print(f'@debug::NY->{text}', file=sys.stderr) #DEBUG

    text = re.sub(r'ق(?! |$)', 'F', text)
    if debug: print(f'@debug::Q->{text}', file=sys.stderr) #DEBUG

    text = REGEX.sub(lambda m: MAPPING[m.group(0)], text)
    if debug: print(f'@debug::C->{text}', file=sys.stderr) #DEBUG

    return text


if __name__ == '__main__':

    parser = ArgumentParser(description='convert arabic text into latin rasm')
    parser.add_argument('input', nargs='?', type=FileType('r'), default=sys.stdin, help='arabic text')
    parser.add_argument('output', nargs='?', type=FileType('w'), default=sys.stdout, help='output file')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    args = parser.parse_args()

    print(ar2latrasm(args.input.read(), args.debug), file=args.output)

