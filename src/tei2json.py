#!/usr/bin/env python3
#
#    tei2json.py
#
# convert TEI to json
#
# dependencies
#   * https://pypi.org/project/tei-reader
#     https://github.com/UUDigitalHumanitieslab/tei_reader
#
# example:
#   $ python tei2json.py ../data/arabic/initial/5_TEI_MS_Q.2-95-106.150-164_BnF_330d_ff.20-21.xml \
#                        ../data/arabic/initial/5_TEI_MS_Q.2-95-106.150-164_BnF_330d_ff.20-21.json
#
# usage:
#   $ cat <edition>.xml | python tei2json.py > <edition>.json
#
#######################################################################################################

import re
import sys
import ujson as json
from bs4 import BeautifulSoup
from argparse import ArgumentParser, FileType


def norm_spaces_meta(s):
    """ strip and normalise spaces in metadata text values.

    Args:
        s (str): text to normalise.

    Return:
        str: noramlised text.

    """
    return re.sub(r'\n{2,}', '\n\n', re.sub(r' +', ' ', s.strip()).replace('\n ', '\n'))


def _getattr(li, name):
    """ get index of item in list li that item[0] equals value of name.

    Args:
        li (list): sequence of two element tuples.
        name (str): name of attrib to find in li.

    Return:
        i (int): index of li where name is found.

    """
    for i, attr in enumerate(li):
        if attr[0] == name:
            return i


def process_gaps(tags_lines, fname):
    """ process info of gap and supplied text.

    Args:
        tags_lines(list): tags along with their attributes and text. Each entry has the following format:
            {'tag':str, 'attribs':list, 'text':str} where attribs is a sequence of 2-element tuples str,str.
        fname (str): file name.

    Yield:
        {'tag' : str, 'attribs' : [(str, str), ...], 'text' : str} -> untouched lines.
        {'tag' : 'gap', 'attribs' : [('unit','surah|ayah|letter'), ('extent', 'i|i-j'), ('supplied', str)] -> lines corresponding to gap(+supplied).

    """
    i, size = 0, len(tags_lines)

    while i < size:

        gap_attribs = {'unit' : None, 'extent' : None, 'supplied' : None}

        # lines not modified
        if tags_lines[i]['tag'] != 'gap':
            yield tags_lines[i]

        # modified lines (gap+supplied)
        else:
            attribs = tags_lines[i]['attribs']
            
            n = len(attribs)

            # attrib /reason/ is required

            j = _getattr(attribs, 'reason')
            
            if attribs[j][1] != 'fragmWit':
                print(f'Error in TEI file {fname}: unexpected value of attrib /reason/: /{attribs[j][1]}/ for tag /gap/', file=sys.stderr) #ERROR
                sys.exit(1)

            # if there are more attribs, these are: /unit/ and /extent/, and both must appear
            if len(attribs) > 1:

                j = _getattr(attribs, 'unit')
                if attribs[j][1] not in ('ayah', 'surah', 'letters'):
                    print(f'Error in TEI file {fname}: unexpected value of attrib /unit/: /{attribs[j][1]}/ for tag /gap/', file=sys.stderr) #ERROR
                    sys.exit(1)
                else:
                    gap_attribs['unit'] = attribs[j][1]
                
                j = _getattr(attribs, 'extent')
                if not re.match(r'^(?:\d|[1-9]\d+)(-(?:\d|[1-9]\d+))?$', attribs[j][1]):
                    print(f'Error in TEI file {fname}: unexpected value of attrib /extent/: /{attribs[j][1]}/ for tag /gap/', file=sys.stderr) #ERROR
                    sys.exit(1)
                else:
                    gap_attribs['extent'] = attribs[j][1]
                
                text_ = tags_lines[i]['text'].strip()
                if text_:
                    print(f'Fatal error: text "{text_}" found after tag gap', file=sys.stderr) #ERROR
                    sys.exit(1)

            # check if supplied comes after
            if i < size-1:
                if tags_lines[i+1]['tag'] == 'supplied':
                    gap_attribs['supplied'] = re.sub(r'[\n ]+', r' ', tags_lines[i+1]['text'])
                i += 1
                    
            yield { 'tag' : 'gap', 'attribs' : list(gap_attribs.items()), 'text' : None}

        i += 1

def process_apps(tags_lines, fname):
    """ process info of apparatus.

    Args:
        tags_lines(list): tags along with their attributes and text. Each entry has the following format:
            {'tag':str, 'attribs':list, 'text':str} where attribs is a sequence of 2-element tuples str,str.
        fname (str): file name.

    Yield:
        {'tag' : str, 'attribs' : [(str, str), ...], 'text' : str} -> untouched lines.
        {'tag' : 'gap', 'attribs' : [('',''), ...] -> lines corresponding to apparatus. #FIXME

    """
    i, size = 0, len(tags_lines)

    while i < size:

        gap_attribs = {'unit' : None, 'extent' : None, 'supplied' : None}

        # lines not modified
        if tags_lines[i]['tag'] != 'app':
            yield tags_lines[i]

        # modified lines (gap+supplied)
        else:
            yield tags_lines[i]

        i += 1


if __name__ == '__main__':

    parser = ArgumentParser(description='parser for TEI DOTS document')
    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin, help='xml file')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='json file')
    args = parser.parse_args()
    
    soup = BeautifulSoup(args.infile.read(), 'xml')
    metadata = soup.teiHeader
    content_tag = soup.find('text').body

    out = {'meta' : {}, 'text' : {}}

    #
    # metadata
    #

    try:
        out['meta']['doc_title'] = norm_spaces_meta(metadata.fileDesc.titleStmt.title.text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.titleStmt.title not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['editor'] = norm_spaces_meta(metadata.fileDesc.titleStmt.respStmt.find('name').text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.titleStmt.respStmt.name not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['ref_text'] = norm_spaces_meta(metadata.fileDesc.editionStmt.edition.text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.titleStmt.editionStmt.edition not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['project'] = norm_spaces_meta(metadata.fileDesc.publicationStmt.authority.text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.titleStmt.publicationStmt.authority not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['country'] = norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.msIdentifier.country.text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.msDesc.msIdentifier.country not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['settlement'] = norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.msIdentifier.find('settlement').text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.msDesc.msIdentifier.settlement not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['repository'] = norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.msIdentifier.find('repository').text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.msDesc.msIdentifier.repository not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['repository'] = norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.msIdentifier.find('repository').text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.msDesc.msIdentifier.repository not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['collection'] = norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.msIdentifier.find('collection').text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.msDesc.msIdentifier.collection not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['idno'] = norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.msIdentifier.find('idno').text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.msDesc.msIdentifier.idno not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['ms_name'] = norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.msIdentifier.find('msName').text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.msDesc.msIdentifier.msName not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['nitems'] = int(norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.find('msContents').msItem['n']))
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.msDesc.msContents.msItems not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['locus'] = norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.find('msContents').msItem.locus.text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.msDesc.msContents.msItem.locus not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['frag_title'] = norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.find('msContents').msItem.find('title').text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.msDesc.msContents.msItem.title not found', file=sys.stderr) #ERROR
        sys.exit(1)

    #FIXME add sub-parsing
    try:
        out['meta']['bibl'] = [norm_spaces_meta(i.text) for i in metadata.fileDesc.find('sourceDesc').msDesc.find('msContents').msItem.find_all('bibl')]
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.msDesc.msContents.msItem.bibl not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['phys_desc'] = norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.find('physDesc').objectDesc.text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.physDesc.objectDesc not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['history'] = norm_spaces_meta(metadata.fileDesc.find('sourceDesc').msDesc.find('history').text)
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.history not found', file=sys.stderr) #ERROR
        sys.exit(1)

    #FIXME add sub-parsing
    try:
        out['meta']['witness_list'] = [{'witness' :  norm_spaces_meta(i.text), 'id' : i['xml:id']}
                                      for i in metadata.fileDesc.find('sourceDesc').find('listWit').find_all('witness')]
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: fileDesc.sourceDesc.listWit not found', file=sys.stderr) #ERROR
        sys.exit(1)

    try:
        out['meta']['notes'] = [{'note' : norm_spaces_meta(i.text), 'date' : i['when']} for i in metadata.find('revisionDesc').find_all('change')]
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: revisionDesc not found', file=sys.stderr) #ERROR
        sys.exit(1)

    #
    # text
    #

    # --- dirty hack, long live to json!! ----

    # check there is content

    try:
        content_tag.text
    except (AttributeError, TypeError):
        print(f'Error in TEI file {args.infile.name}: text.body not found', file=sys.stderr) #ERROR
        sys.exit(1)

    content = str(content_tag)

    # remove body tag and comments
    content_str_clean = re.sub(r'<!--.+?-->', '', content, flags=re.DOTALL).replace('<body>', '').replace('</body>', '')

    # check that the first tag is pb and it is directly followed by another tag (not text)
    if not re.match(r'<pb[^>]+><', re.sub(r'[ \n]', r'', content_str_clean)):
        print(f'Error in TEI file {args.infile.name}: body does not start with pb directly followed by another tag', file=sys.stderr) #ERROR
        sys.exit(1)

    # parse tags

    # ----------
    # groupby pb
    # ----------

    pbs = [(p.strip(), r.strip()) for p,r in re.findall(r'<pb(.+?)/>(.+?)(?=<pb|$)', content_str_clean, flags=re.DOTALL)]

    pbs_out = list({'n' : -1, 'gap' : None, 'storage' : None, 'source' : None, 'content' : None} for i in range(len(pbs)))

    for i, (pb, rest) in enumerate(pbs):
        attribs = pb.split()

        if not attribs:
            print(f'Error in TEI file {args.infile.name}: format of tag "{pb_tag}": tag is empty', file=sys.stderr) #ERROR
            sys.exit(1)
    
        # +/- page
        elif len(attribs) == 1:

            m = re.match(r'n="(\d+[rv])([\-+])"', attribs[0])
            if not m:
                print(f'Error in TEI file {args.infile.name}: format of tag "{pb_tag}"', file=sys.stderr) #ERROR
                sys.exit(1)
            pbs_out[i]['n'] = m.group(1)
            pbs_out[i]['gap'] = m.group(2)

        # page with image ; attrib n is required, attribs facs and source are optional
        else:
            
            n_attrib_found = False
            #FIXME actualizar cuando conda distribuya de una *** vez python 8...
            for attrib in attribs:
                m = re.match(r'facs="(.+.jpg)"', attrib)
                if m:
                    pbs_out[i]['facs'] = m.group(1)
                    continue
                m = re.match(r'source="(.+)"', attrib)
                if m:
                    pbs_out[i]['source'] = m.group(1)
                    continue
                m = re.match(r'n="(\d+[rv])"', attrib)
                if m:
                    n_attrib_found = True
                    pbs_out[i]['n'] = m.group(1)
                    continue
                
                print(f'Error in TEI file {args.infile.name}: format of tag "{pb_tag}", unkown attrib "{attrib}"', file=sys.stderr) #ERROR

            if not n_attrib_found:
                print(f'Error in TEI file {args.infile.name}: format of tag "{pb_tag}", attrib n is missing', file=sys.stderr) #ERROR


        # remove closing tags from content after pb
        rest = re.sub(r'</.+?>', r'', rest)

        # parse rest of tags that follow pb and their attribs and text until the next pb tag
        inner_info = [(tagi.strip().split(), texti.strip()) for tagi, texti in re.findall(r'<(.+?)>(.+?)(?=<|$)', rest, flags=re.DOTALL)]


        inner = [{'tag' : tagi, 'attribs' : ([] if r==[] else [re.match(r'(.+)="(.+)"', at).groups() for at in r]), 'text' : re.sub(r'[\n ]+', r' ', texti)} for
                ((tagi, *r), texti) in inner_info]

        inner_proc_gaps = list(process_gaps(inner, args.infile.name))
        inner_proc_app = list(process_apps(inner_proc_gaps, args.infile.name))
        
        pbs_out[i]['inner'] = inner_proc_app

    #
    # re-organise info
    #

    for pinfo in pbs_out:
        print('\n----------------------------------------------------------------------------------------------------') #DEBUG
        print(f"n={pinfo['n']} gap={pinfo['gap']} storage={pinfo['storage']} source={pinfo['source']}") #DEBUG

        for item in pinfo['inner']:

            print('item::', item)

    #json.dump(out, args.outfile, ensure_ascii=False)

