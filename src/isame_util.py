#!/usr/bin/env python3
#
#    isame_util.py
#
# utilify functions and constacts for isame processors
#
######################################################

import re
import sys
from bs4 import BeautifulSoup

CUSTOM_MAPPING = {
    'ك'   : 'ک',
    'ᵃⁿA' : 'Aᵃⁿ',
    'ᵃᵐA' : 'Aᵃᵐ',
    'ـ' : '', # remove tatweel
}

HIST_ORIGIN = {
    'F' : 'Fustat',
    'D' : 'Damascus',
    'S' : 'Sanaa',    # not included in InterSaME
    'K' : 'Kairouan', # not included in InterSaME
    'U' : 'Unknown'
}

VOWELS = ('ᵃ', 'ᵘ', 'ᵢ', 'ᵚ', 'ᵒ', 'ᵃⁿ', 'ᵘⁿ', 'ᵃᵐ', 'ᵘᵐ', 'ᵢₙ', 'ᵢₘ')
ARCH = 'ABGDRSCTEFQKLMNHWY'
ARDW = 'ARDW'
BLOCK_START = ARDW+'#'
LINE_FILLER = '―'
EMPTY_SET = '∅'
NOTES_TAGS = ('dots', 'layers', 'palaeog', 'reading', 'codic', 'ortho')

REPL_ISAME = {'¹':'’',
              '²':'’’',
              '³':'’’’',
              '₁':',',
              '₂':',,',
              '₃':',,,',
}

TO_ISAME_REGEX = re.compile('|'.join(REPL_ISAME))

#           sura : number of verses
NUM_VERSES = { 1 :   7 ,
               2 : 286 ,
               3 : 200 ,
               4 : 176 ,
               5 : 120 ,
               6 : 165 ,
               7 : 206 ,
               8 :  75 ,
               9 : 129 ,
              10 : 109 ,
              11 : 123 ,
              12 : 111 ,
              13 :  43 ,
              14 :  52 ,
              15 :  99 ,
              16 : 128 ,
              17 : 111 ,
              18 : 110 ,
              19 :  98 ,
              20 : 135 ,
              21 : 112 ,
              22 :  78 ,
              23 : 118 ,
              24 :  64 ,
              25 :  77 ,
              26 : 227 ,
              27 :  93 ,
              28 :  88 ,
              29 :  69 ,
              30 :  60 ,
              31 :  34 ,
              32 :  30 ,
              33 :  73 ,
              34 :  54 ,
              35 :  45 ,
              36 :  83 ,
              37 : 182 ,
              38 :  88 ,
              39 :  75 ,
              40 :  85 ,
              41 :  54 ,
              42 :  53 ,
              43 :  89 ,
              44 :  59 ,
              45 :  37 ,
              46 :  35 ,
              47 :  38 ,
              48 :  29 ,
              49 :  18 ,
              50 :  45 ,
              51 :  60 ,
              52 :  49 ,
              53 :  62 ,
              54 :  55 ,
              55 :  78 ,
              56 :  96 ,
              57 :  29 ,
              58 :  22 ,
              59 :  24 ,
              60 :  13 ,
              61 :  14 ,
              62 :  11 ,
              63 :  11 ,
              64 :  18 ,
              65 :  12 ,
              66 :  12 ,
              67 :  30 ,
              68 :  52 ,
              69 :  52 ,
              70 :  44 ,
              71 :  28 ,
              72 :  28 ,
              73 :  20 ,
              74 :  56 ,
              75 :  40 ,
              76 :  31 ,
              77 :  50 ,
              78 :  40 ,
              79 :  46 ,
              80 :  42 ,
              81 :  29 ,
              82 :  19 ,
              83 :  36 ,
              84 :  25 ,
              85 :  22 ,
              86 :  17 ,
              87 :  19 ,
              88 :  26 ,
              89 :  30 ,
              90 :  20 ,
              91 :  15 ,
              92 :  21 ,
              93 :  11 ,
              94 :   8 ,
              95 :   8 ,
              96 :  19 ,
              97 :   5 ,
              98 :   8 ,
              99 :   8 ,
             100 :  11 ,
             101 :  11 ,
             102 :   8 ,
             103 :   3 ,
             104 :   9 ,
             105 :   5 ,
             106 :   4 ,
             107 :   7 ,
             108 :   3 ,
             109 :   6 ,
             110 :   3 ,
             111 :   5 ,
             112 :   4 ,
             113 :   5 ,
             114 :   6 
}

SURA_NAMES = {  1  : 'Al-Fatiha',
                2  : 'Al-Baqarah',
                3  : 'Al-Imran',
                4  : 'An-Nisa',
                5  : 'Al-Ma\'idah',
                6  : 'Al-An\'am',
                7  : 'Al-A\'raf',
                8  : 'Al-Anfal',
                9  : 'At-Tawbah',
                10 : 'Yunus',
                11 : 'Hud',
                12 : 'Yusuf',
                13 : 'Ar-Ra\'d',
                14 : 'Ibrahim',
                15 : 'Al-Hijr',
                16 : 'An-Nahl',
                17 : 'Al-Isra',
                18 : 'Al-Kahf',
                19 : 'Maryam',
                20 : 'Ta-Ha',
                21 : 'Al-Anbiya',
                22 : 'Al-Hajj',
                23 : 'Al-Mu\'minun',
                24 : 'An-Nur',
                25 : 'Al-Furqan',
                26 : 'Ash-Shu\'ara',
                27 : 'An-Naml',
                28 : 'Al-Qasas',
                29 : 'Al-Ankabut',
                30 : 'Ar-Rum',
                31 : 'Luqmaan',
                32 : 'As-Sajda',
                33 : 'Al-Ahzaab',
                34 : 'Saba',
                35 : 'Faatir',
                36 : 'Yaseen',
                37 : 'As-Saaffaat',
                38 : 'Saad',
                39 : 'Az-Zumar',
                40 : 'Ghafir',
                41 : 'Fussilat',
                42 : 'Ash_Shooraa',
                43 : 'Az-Zukhruf',
                44 : 'Ad-Dukhaan',
                45 : 'Al-Jaathiyah',
                46 : 'Al-Ahqaaf',
                47 : 'Muhammad',
                48 : 'Al-Fath',
                49 : 'Al-Hujuraat',
                50 : 'Qaaf',
                51 : 'Adh-Dhaariyaat',
                52 : 'At-Toor',
                53 : 'An-Najm',
                54 : 'Al-Qamar',
                55 : 'Ar-Rahman',
                56 : 'Al-Waqi\'a',
                57 : 'Al-Hadeed',
                58 : 'Al-Mujadila',
                59 : 'Al-Hashr',
                60 : 'Al-Mumtahanah',
                61 : 'As-Saff',
                62 : 'Al-Jumu\'ah',
                63 : 'Al-Munafiqoon',
                64 : 'At-Taghabun',
                65 : 'At-Talaq',
                66 : 'At-Tahreem',
                67 : 'Al-Mulk',
                68 : 'Al-Qalam',
                69 : 'Al-Haaqqa',
                70 : 'Al-Ma\'aarij',
                71 : 'Nooh',
                72 : 'Al-Jinn',
                73 : 'Al-Muzzammil',
                74 : 'Al-Muddaththir',
                75 : 'Al-Qiyamah',
                76 : 'Al-Insaan',
                77 : 'Al-Mursalaat',
                78 : 'An-Naba\'',
                79 : 'An-Naazi\'aat',
                80 : 'Abasa',
                81 : 'At-Takweer',
                82 : 'Al-Infitar',
                83 : 'Al-Mutaffifeen',
                84 : 'Al-Inshiqaaq',
                85 : 'Al-Burooj',
                86 : 'At-Taariq',
                87 : 'Al-A\'laa',
                88 : 'Al-Ghaashiyah',
                89 : 'Al-Fajr',
                90 : 'Al-Balad',
                91 : 'Ash-Shams',
                92 : 'Al-Layl',
                93 : 'Ad-Dhuha',
                94 : 'Ash-Sharh',
                95 : 'At-Teen',
                96 : 'Al-Alaq',
                97 : 'Al-Qadr',
                98 : 'Al-Bayyinahh',
                99 : 'Az-Zalzalah',
               100 : 'Al-\'Aadiyaat',
               101 : 'Al-Qaari\'ah',
               102 : 'At-Takaathur',
               103 : 'Al-\'Asr',
               104 : 'Al-Humazah',
               105 : 'Al-Feel',
               106 : 'Quraysh',
               107 : 'Al-Maa\'oon',
               108 : 'Al-Kawthar',
               109 : 'Al-Kaafiroon',
               110 : 'An-Nasr',
               111 : 'Al-Masad',
               112 : 'Al-Ikhlaas',
               113 : 'Al-Falaq',
               114 : 'Al-Naas',
}

# Taken from the rasm-arch library - https://pypi.org/project/rasm-arch/
ARABIC_CHARS_MAPPING = {
    'Q' : 'ٯ' ,
    'N' : 'ں' ,
    'Y' : 'ى' ,
    'A' : 'ا' ,
    'B' : 'ٮ' ,
    'G' : 'ح' ,
    'R' : 'ر' ,
    'D' : 'د' ,
    'T' : 'ط' ,
    'C' : 'ص' ,
    'S' : 'س' ,
    'F' : 'ڡ' ,
    'E' : 'ع' ,
    'W' : 'و' ,
    'H' : 'ه' ,
    'M' : 'م' ,
    'L' : 'ل' ,
    'K' : 'ك' ,  # ک
    'ᵢ' : 'ِ' ,
    'ᵃ' : 'َ' ,
    'ᵘ' : 'ُ' ,
    'ᵚ' : 'ّ' ,
    'ᵒ' : 'ۡ' ,
    'ˀ' : 'ٔ' ,
    'ɂ' : 'ٕ' ,
    'ʔ' : 'ء' ,
    '˜' : 'ٓ' ,
    'ᴬ' : 'ٰ' ,
    'ʸ' : 'ۦ' ,
    'ʷ' : 'ۥ'  ,
    '⒮' : 'ۖ' ,
    '⒬' : 'ۗ' ,
    '⒨' : 'ۘ' ,
    '⒧' : 'ۙ' ,
    '⒥' : 'ۚ' ,
    '∴' : 'ۛ' ,
    '-' : '' ,  #FIXME revisa
    '!' : '' ,
    '©' : '' ,
    '≠' : '' ,
    '←' : '' ,
    '↑' : '' ,
    '→' : '' ,
    '↓' : '' ,
    '↔' : '' ,
    '↕' : '' ,
}

ARABIC_MAPPING = {
    'ه’’'  : 'ة' ,
    'ٮ’’’' : 'ث' ,
    'ٮ’’'  : 'ت' ,
    'ٮ,,'  : 'ي' ,
    'ٮ,'   : 'ب' ,
    'ٮ’'   : 'ن' ,
    'ں’'   : 'ن' ,
    'ح,'   : 'ج' ,
    'ح’'   : 'خ' ,
    'ٯ’’'  : 'ق' ,
    'ڡ’’'  : 'ق' ,
    'ڡ’'   : 'ف' ,
    'ڡ,'   : 'ڢ' ,
    'ٯ’'   : 'ڧ' ,
    'اᵟ'   :  'ٱ' ,
    'أ'    : 'أ' ,
    'إ'    : 'إ' ,
    'آ'    : 'آ' ,
    'س’’’' : 'ش' ,
    'س,,,' : '࣭࣭࣭' ,
    'ص’'   : 'ض' ,
    'ط’'   : 'ظ' ,
    'د’'   : 'ذ' ,
    'ر’'   : 'ز' ,
    'ع’'   : 'غ' ,
    'ى⇒'   : 'ے' ,
    'َⁿ'   : 'ً' ,
    'ُⁿ'   : 'ٌ' ,
    'ِₙ'   : 'ٍ' ,
    'ََ'    : 'ࣰ' ,
    'ُُ'    : 'ࣱ' ,
    'ِِ'    : 'ࣲ' ,
    'َᵐ'   : 'َۢ' ,
    'ُᵐ'   : 'ُۢ' ,
    'ِₘ'   : 'ِۭ' ,
    '+ۥ'    : 'ۥ' ,
    '+ٰ'    : 'ٰ' ,
    '+ٔ'    : 'ٔ' , 
    '’'    : '࣪' ,
    ','    : '࣭' ,
}

ARABIC_CHARS_REGEX = re.compile('|'.join(map(re.escape, ARABIC_CHARS_MAPPING)))
ARABIC_REGEX = re.compile('|'.join(map(re.escape, ARABIC_MAPPING)))

def calculate_line(lines, ibloc):
    """ calculate line where current block is located.

    Args:
        lines (list): sequence of line elements:
            {"num" : int, "inib" : int}
        iblock (int): position of current block

    Return:
        float: number of line. If line is, e.g., between 1 and 2,
            its number would be 1.5.

    """
    prev_ini, line = -1, None
    for li in lines:
        if ibloc >= prev_ini and ibloc < li['inib']:
            break
        line = li['num']
        prev_ini = li['inib']                        
    return line


def word_sub_variant(variants, ibloc, ichar):
    """ check if there is a variant in position ibloc,ichar containing a word subdivision (#)

    Args:
        variants (list): variants annotated. Each item has the following structure:
                        { "inib": int,
                          "inic": int,
                          "endb": int,
                          "endc": int,
                          "ref" : str,
                          "stc" : str,
                          "typ" : str
                        }
        ibloc (int): block to check if there is a word_sub variant.
        ichar (int): character to check if there is a word_sub variant.

    Return:
        bool: True if there is a word_sub variant in ibloc,ichar position,
            False otherwise.

    """
    for var in variants:
        if var['inib'] == var['endb'] == ibloc and var['inic'] == var['endc'] == ichar and var['ref']=='#':
            return True
    return False

def diff_variant(variants, btok, ibloc, logging, debug=False):
    """ Calculate the shape of btok in case it is included in a variant, so that we recreate the reference
    text as annotated.

    Args:
        variants (list): variants annotated. Each item has the following structure:
                        { "inib": int,
                          "inic": int,
                          "endb": int,
                          "endc": int,
                          "ref" : str,
                          "stc" : str,
                          "typ" : str,
                          "lay" : str
                        }
        btok (str): current block.
        ibloc (int): index to current block.
        logging (logging): object for writing loggings.
        debug (bool): show debug info in logging file.

    Return:
        str, [(str, str), ...]: btok reshaped as the reference, or btok as such when there was no variant;
            and typology and category of variant(s). Typically there is only one variant, but there can be more.
            If no variant btok, None is returned.

    """
    for i in range(len(variants)-1,-1,-1):

        var = variants[i]
        
        # btok had a variant inside; block btok==ABC in A[B/ref]C
        if var['inib'] == var['endb'] == ibloc:
            if debug:
                logging.debug(f'~~ A. btok containing both start and end of variant ({var["stc"]}, {var["typ"]})')
            
            aux = btok[:var['inic']] + var['ref'] + btok[var['endc']+1:], [(var['stc'], var['typ'])]

            # there might be more variants within the same block, e.g. #ME[∅/A=r=long.vwl.noun]B’+’M[../∅=vd=tanwin]#
            j = i
            while (j:=j-1)>=0:
                prev_var = variants[j]
                if prev_var['inib'] == prev_var['endb'] == ibloc:
                    if debug:
                        logging.debug(f'~~ A-2. btok containing both start and end of variant ({var["stc"]}, {var["typ"]})')

                    aux = aux[0][:prev_var['inic']] + prev_var['ref'] + aux[0][prev_var['endc']+1:], [(prev_var['stc'], prev_var['typ'])] + aux[1]
            return aux

        # block has a variant that starts in it and continues to later blocks; block btok==A in [AB/ref]
        elif var['inib'] == ibloc and var['endb'] > ibloc:
            for iref, c in enumerate(var['ref']):
                if c in BLOCK_START:
                    break
            if debug:
                logging.debug(f'~~ B. btok containing start of variant ({var["stc"]}, {var["typ"]})')
            return btok[:var['inic']] + var['ref'][:iref], [(var['stc'], var['typ'])]

        elif var['inib'] < ibloc:

            nprev_blocks = ibloc - var['inib']
            cnt = 0
            for iref, c in enumerate(var['ref']):
                if c in BLOCK_START:
                    cnt += 1
                if cnt == nprev_blocks:
                    break

            # block has a variant that starts in previous block(s) and ends in the block we are currently reading; block btok==B in [AB/ref]
            if var['endb'] == ibloc:
                if debug:
                    logging.debug(f'~~ C. btok containing end of variant ({var["stc"]}, {var["typ"]})')
                return var['ref'][iref:] + btok[var['endc']:], [(var['stc'], var['typ'])]

            # btok is in the middle of a variant; block btok==B in [ABC/ref]
            elif var['endb'] > ibloc:

                nnext_blocks = var['endb'] - ibloc
                cnt = 0
                for iref_end, c in enumerate(var['ref'][::-1]):
                    if c in BLOCK_START:
                        cnt += 1
                    if cnt == nnext_blocks:
                        break
                if debug:
                    logging.debug(f'~~ D. btok is inside a variant that starts and end in surrounding blocks ({var["stc"]}, {var["typ"]})')
                return var['ref'][iref:iref_end+1], [(var['stc'], var['typ'])]

    return btok, None

def get_metadata_table(filename):
    """ read wiki table from filename and extract association of repository names and signatures.

    Args:
        filename(str): file to parse.

    Return:
        dict: mapping of siganture to its repository information. Each element has the following format:
          {<sig>: {'Hist.ID': <hist_id>,
                   'Period': <period>,
                   'Hands': <hands>,
                   'Support': <support>,
                   'Ink': <ink>,
                   'Leaf Dim.': <leaf_dimensions>,
                   'Lines per page': <liens_page>,
                   'Script Style': <script_style>,
                   'Ms.frgmt ID': <sig>,
                   'Folia': <folia>,
                   'Repository',: <repo>
                   'Location': <loc>,
                   'Editor': <editor>,
                   'Transcriber': <transcriber>,
                   'Reviewer': <reviewer>,
                   'Start': <start_date>,
                   'End': <end_date>
                   }
            }

    """
    from pprint import pprint
    with open(filename) as fp:
        soup = BeautifulSoup(fp.read(), 'html.parser')

        table = [[row.text.strip() for row in tr.find_all(['td','th'])] for tr in soup.find_all('tr')]

        headers = table[0]
        nheader = len(headers)

        for i in range(1, len(table)):
            nrow = len(table[i])
            if nrow != len(headers):
                table[i] = table[i-1][:nheader-nrow]+table[i]

        return {row[headers.index('Ms.frgmt ID')]:dict(zip(headers, row)) for row in table}

def to_isame_trans(s):
    """ convert paleo-orthographic representation of consonantal diacritics from the rasm library to InterSaME

    Args:
        s(str): string to modify.

    Return:
        str: modified string.

    """
    return TO_ISAME_REGEX.sub(lambda m: REPL_ISAME[m.group(0)], s)


def split_blocks(s):
    """ split a string s into blocks

    """
    aux = []
    for c in s:
        aux.append(c)
        if c in 'ARDW':
            yield ''.join(aux)
            aux = []
    yield ''.join(aux)

def absent_text(ibloc, ichar, illegible, lacunas):
    """ check if the position indicated by block and char indexes is inside illegible or a lacuna marks.

    Args:
        ibloc (int): position within the blocks.
        ichar (int): position within the chars of the blocks
        illegible (list): structure containing the information of the illegible sequences. Each element contains:
            {"inib": int, "inic": int, "endb": int, "endc": int}
        lacuna (list): structure containing the information of the lacuna sequences. Each element contains:
            {"inib": int, "inic": int, "endb": int, "endc": int}

    Return:
        bool: True if the position pointed to is marked as illegible/lacuna, False otherwise.

    """
    for struct in (illegible, lacunas):
        for elem in struct:
            if elem['inib'] < ibloc and elem['endb'] > ibloc:
                return True
            elif elem['inib'] == ibloc and elem['endb'] > ibloc and elem['inic'] <= ichar:
                return True
            elif elem['inib'] < ibloc and elem['endb'] == ibloc and elem['endc'] >= ichar:
                return True
            elif elem['inib'] == ibloc and elem['endb'] == ibloc and \
                elem['inic'] <= ichar and elem['endc'] >= ichar:
                return True
    return False
