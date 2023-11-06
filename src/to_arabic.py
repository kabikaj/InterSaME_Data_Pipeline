#!/usr/bin/env python3
#
#    to_arabic.py
#
# convert Latin paleographic representation to Arabic script
#
# usage:
#   $ cat ../../data/arabic/transcriptions/F002_Q.23.80-46.25_frgm_14ff.txt | python to_arabic.py --rm_cons_strokes
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

MAPPING_RASM1 = {
    'Q' : 'ٯ' ,
    'N' : 'ں' ,
    'Y' : 'ي' ,  ##### ARABIC YA

    'B’' : 'ٮ' ,
    'B’’' : 'ٮ' ,
    'B’’’' : 'ٮ' ,
    'B,' : 'ٮ',
    'B,,' : 'ٮ',

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


def to_arabic(tok, space=' ', debug=False, html=False, varr=False):
    """
    Convert the InterSaME Transcription back into Arabic script

    Args:
        tok (str): text.
        space (string): character used for indicating space.
        debug (bool): show debugging info.

    Return:
        str: modified text.
    """
    if debug: print(f'@DEBUG[1]@ {tok}', file=sys.stderr) #TRACE


    if html:

            tok = re.sub("&rsquo;", "’", tok)    
            tok = re.sub("&rsquo;", "’", tok)    
            tok = re.sub("&rarr;", "→", tok)    
            tok = re.sub("&darr;", "↓", tok)    
            tok = re.sub("&uarr;", "↑", tok)    
            tok = re.sub("&larr;", "←", tok)    
            #tok = re.sub("", "↕", tok)    
            tok = re.sub("&harr;", "↔", tok)    
            tok = re.sub("&dArr;", "⇓", tok)    
            tok = re.sub("&rArr;", "⇒", tok)    
            tok = re.sub("&copy;", "©", tok)    
            tok = re.sub("&empty;", "∅", tok)    
            tok = re.sub("&ne;", "≠", tok)
            tok = re.sub("&deg;", "°", tok)

            #tok = re.sub("", "ᵒˀᴬⁿ―ʸ", tok)    

            #change / to = for matching issues
            #tok = re.sub("r/spell.", "r=spell.", tok)            

            # replace different versions
            # Read 1 % Read 2 (Ref)
            # replace % later into /
            if varr:
                tok = re.sub(r'(<span [^>]*?)>([^>]*?)\^([^>]*?)/([^>]*?)(</span>)', rf'\2 @\3 (\4)', tok)
            else:
                tok = re.sub(r'(<span [^>]*?)>([^>]*?)\^([^>]*?)/([^>]*?)(</span>)', rf'\2', tok)


            # replace variant reading
            # MSS version followed by (Ref)
            # keep empty sign
            if varr:
                tok = re.sub(r'(<span [^>]*?)>([^<]*?)/((.)+?)(</span>)', rf'\2 (\3)', tok)
            else:
                tok = re.sub(r'(<span [^>]*?)>([^<]*?)/((.)*?)(</span>)', rf'\2', tok)


            # remove span for locus
            tok = re.sub(r'(<span data-dpt="location" [^>]*?)>((.)*?)(</span>)', '', tok)


            # remove span for notes
            tok = re.sub(r'(<span data-dpt="note_" [^>]*?)>((.)*?)(</span>)', rf'\2', tok)

            # remove span for divider
            tok = re.sub(r'(<span data-dpt="divider" [^>]*?)>((.)*?)(</span>)', rf'[\2]', tok)

            # remove all other span
            # lacuna, varr(r/spell.vwl?), unclear
            tok = re.sub(r'(<span [^>]*?)>((.)*?)(</span>)', rf'\2', tok)

            tok = re.sub("%", '/', tok)



    # remove notes
    tok = re.sub(r'Notes:', '', tok)
    tok = re.sub(r'\|L[0-9]+.*', '', tok)

    # remove Source
    tok = re.sub(r'Source.*', '', tok)


    

    if not html:
        # remove variant reading
        # simple version keeps letter before /
        # works for severals variants in the same line
        if debug: print(f'@DEBUG[2]@ {tok.count("/")}', file=sys.stderr) #TRACE
        
        for i in range(tok.count("/")):
            tok = re.sub(r'(\| [0-9]\| [^/\n]*)/(.)?', rf'\1', tok)
        

        # remove versions reading
        # simple version keeps letter before ^
        # works for severals variants in the same line
        if debug: print(f'@DEBUG[3]@ {tok.count("^")}', file=sys.stderr) #TRACE
        
        for i in range(tok.count("^")):
            tok = re.sub(r'(\| [0-9]\| [^/\n]*)\^(.)?', rf'\1', tok)


    """
    tok = re.sub(r'([بج])', rf'\1{STROKE_BELOW}', tok)
    if debug: print(f'@DEBUG[2]@ {tok}', file=sys.stderr) #TRACE
    tok = re.sub(r'([خذزنضظغف])', rf'\1{STROKE_ABOVE}', tok)
    """

    # remove symbolsnotes
    tok = re.sub(r'[→←↑↓↕↔©!\-―≠]', '', tok)
    if not varr:
        tok = re.sub(r'[∅ᵒˀᴬⁿʸ°]', '', tok)

    # replace symbol by symbol
    tok = re.sub("B,,", "\u064a", tok)
    tok = re.sub("B,", "\u0628", tok)
    tok = re.sub("B’’’", "\u062b", tok)
    tok = re.sub("B’’", "\u062a", tok)
    tok = re.sub("B’", "\u0646", tok)
    tok = re.sub("B", "\u066e", tok)

    tok = re.sub("N’", "\u0646", tok)
    tok = re.sub("N", "\u06ba", tok)
 
    tok = re.sub("F,", "\u06a2", tok)
    tok = re.sub("F’’", "\u0642", tok)
    tok = re.sub("F’", "\u0641", tok)
    tok = re.sub("F", "\u06a1", tok)
    
    tok = re.sub("Q’’", "\u0642", tok)
    tok = re.sub("Q", "\u066f", tok)
    tok = re.sub("Y’’", "\u064a", tok)
    tok = re.sub("Y,,", "\u064a", tok)
    
    tok = re.sub("Y⇓", "\u06cc", tok)
    tok = re.sub("Y⇒", "\u06d2", tok)
    tok = re.sub("Y", "\u06cc", tok)
 
    tok = re.sub("G’", "\u062e", tok)
    tok = re.sub("G,", "\u062c", tok)
    tok = re.sub("G", "\u062d", tok)

    tok = re.sub("D’", "\u0630", tok)
    tok = re.sub("D", "\u062f", tok)

    tok = re.sub("R’", "\u0632", tok)
    tok = re.sub("R", "\u0631", tok)

    tok = re.sub("S’’’", "\u0634", tok)
    tok = re.sub("S", "\u0633", tok)

    tok = re.sub("C’", "\u0636", tok)
    tok = re.sub("C", "\u0635", tok)

    tok = re.sub("T’", "\u0638", tok)
    tok = re.sub("T", "\u0637", tok)

    tok = re.sub("E’", "\u063a", tok)
    tok = re.sub("E", "\u0639", tok)

    tok = re.sub("K", "\u06a9", tok)
    #isolated/final 06A9 in the option --KP Kaf parallel 06AA
    #initial/middle 0643

    tok = re.sub("L", "\u0644", tok)
    tok = re.sub("M", "\u0645", tok)
    tok = re.sub("H", "\u0647", tok)
    tok = re.sub("W", "\u0648", tok)

    tok = re.sub("A", "\u0627", tok)
    tok = re.sub("ᵃᵃ", "\u064b", tok)
    tok = re.sub("ᵃ", "\u064e", tok)
    tok = re.sub("ᵘᵘ", "\u064c", tok)
    tok = re.sub("ᵘ", "\u064f", tok)
    tok = re.sub("ᵢᵢ", "\u064d", tok)
    tok = re.sub("ᵢ", "\u0650", tok)


    #Sura ending
    #5vv> remove 1, keep letter HA
    #10w> flower like star \u066D
    #number of tens: FD3E and FD3F for ornated parenthesis include number

    tok = re.sub("#", ' ', tok)

    # convert simple mapping
    # tok = REGEX_TRANS.sub(lambda m: MAPPING_TOARAB[m.group(0)], tok)

    return tok


if __name__ == '__main__':

    parser = ArgumentParser(description='convert Arabic script o Latin paleographic representation')
    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin, help='input file')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='output file')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    parser.add_argument('--html', action='store_true', help='html input')
    parser.add_argument('--varr', action='store_true', help='handling of variants and modifications')
    
    args = parser.parse_args()

    for line in (l.strip() for l in args.infile):
        #line.replace('Notes:', '')
        #print(to_arabic(line, debug=args.debug), file=args.outfile)
        #print(line.replace('_', '%%'), file=args.outfile)
        #print(line.replace('ـ', ''), file=args.outfile)

        if args.html:
            line = re.sub("<p>", "", line)
            line = re.sub("</p>", "", line)
            line = re.sub("&nbsp;", "\n\r", line)
            line = re.sub("<br />", "", line)

            #if ("locus" in line): #removes complete line; missing linebreak before locus removes last line of previous page
            #    continue


        if line.startswith('TITLE'):
            print(line, file=args.outfile)
        else:
            print(to_arabic(line, debug=args.debug, html=args.html, varr=args.varr), file=args.outfile)
            #print("\u0633", file=args.outfile)


