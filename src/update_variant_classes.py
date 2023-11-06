#!usr/bin/env python3
#
#    update_variant_classes.py
#
# update new tags in xml transcriptions exported from Archetype
#
# TODO check F007 BnF.Ar.330d
#
# usage:
#   $ cat ../../data/arabic/trans/F001_BnF.Ar.330f-3-trans.xml | python update_variant_classes.py
#   $ cat ../../data/arabic/trans/F001_OIC.A6961-3-trans.xml | python update_variant_classes.py
#   $ cat ../../data/arabic/trans/F003_BnF.Ar.330b-3-trans.xml | python update_variant_classes.py
#   $ cat ../../data/arabic/trans/F004_BnF.Ar.329b-3-trans.xml | python update_variant_classes.py
#   $ cat ../../data/arabic/trans/F005_BnF.Ar.329c-3-trans.xml | python update_variant_classes.py
#   $ cat ../../data/arabic/trans/F017_BnF.Ar.340f-3-trans.xml | python update_variant_classes.py
#   $ cat ../../data/arabic/trans/D001_UbT.Ma.VI.165-3-trans.xml | python update_variant_classes.py
#   $ cat ../../data/arabic/trans/D003_CUL.Add.1125-3-trans.xml | python update_variant_classes.py
#
###################################################################################################

import re
import sys
from argparse import ArgumentParser, FileType

REPL = {"<span data-dpt=\"varr\" data-dpt-type=\"cd/unknown\">": "<span data-dpt=\"varcd\" data-dpt-type=\"cd/unknown\">",
        "<span data-dpt=\"varsub\" data-dpt-type=\"sub/sub.words\">": "<span data-dpt=\"varsub\" data-dpt-type=\"sub/words\">",
        "<span data-dpt=\"divider\" data-dpt-type=\"hundred\">": "<span data-dpt=\"divider\" data-dpt-type=\"miaa\">",
        "<span data-dpt=\"varvd\" data-dpt-type=\"vd/wasl\">": "<span data-dpt=\"varvd\" data-dpt-type=\"vd/alif.al.wasl\">",
        "r/harf": "r/lexicon.harf",
        "r/haplog": "r/mech.haplog",
        "r/ibdal": "r/lexicon.ibdal",
        "r/vrb.frm.i-iii": "r/lexicon.vrb.forms",
        "r/ta.marb": "r/spell.ta.marb",
        "r/long.vwl.dual": "r/spell.vwl.A.dual",
        "r/long.vwl.fm.plur": "r/spell.vwl.A.fm.pl",
        "r/long.vwl.harf": "r/spell.vwl.AYW",
        "r/long.vwl.noun": "r/spell.vwl.AYW",
        "r/long.vwl.prep": "r/spell.vwl.AYW",
        "r/long.vwl.pron": "r/spell.vwl.AYW",
        "r/long.vwl.verb": "r/spell.vwl.AYW",
        "r/long.a.Y-A": "r/spell.vwl.long.a.A-Y",
        "r/agreem": "r/synt.agreem",
        "r/pronoun": "r/synt.pron",
        "r/sg-plur": "r/synt.sg.pl.dual",
        "r/vrb.Impf-Perf": "r/synt.verb.tense",
        "r/pron.hm.ha": "r/vwl.h.pron",
        "r/pron.h.kinaya": "r/vwl.h.pron",
        "r/imala": "r/vwl.imala",
        "r/pron.pl.mim.u": "r/vwl.u.mim.pron",
        "r/yaat.al.idafa": "r/vwl.y.pron",
        "cd/harf": "cd/lexicon.harf",
        "cd/haplog": "cd/mech.haplog",
        "cd/ibdal": "cd/lexicon.ibdal",
        "cd/ta.marb": "cd/spell.ta.marb",
        "cd/long.vwl.dual": "cd/spell.vwl.A.dual",
        "cd/long.vwl.harf": "cd/spell.vwl.AYW",
        "cd/long.vwl.noun": "cd/spell.vwl.AYW",
        "cd/long.vwl.prep": "cd/spell.vwl.AYW",
        "cd/long.vwl.pron": "cd/spell.vwl.AYW",
        "cd/long.vwl.verb": "cd/spell.vwl.AYW",
        "cd/long.a.Y-A": "cd/spell.vwl.long.a.A-Y",
        "cd/pronoun.impf.N-Y": "cd/synt.pron",
        "cd/pronoun.impf.T-N": "cd/synt.pron",
        "cd/pronoun.impf.T-Y": "cd/synt.pron",
        "cd/pronoun.impf.Y-N": "cd/synt.pron",
        "cd/pronoun.impf.Y-T": "cd/synt.pron",
        "cd/LA.u": "cd/unclass.LA",
        "cd/Ylong.a": "cd/spell.vwl.long.a.A-Y",
        "cd/yaat.al.idafa": "cd/vwl.y.pron",
        "vd/harf": "vd/lexicon.harf",
        "vd/haplog": "vd/mech.haplog",
        "vd/vrb.frm.iv-vi": "vd/lexicon.vrb.forms",
        "vd/long.vwl.dual": "vd/spell.vwl.A.dual",
        "vd/long.vwl.fm.plur": "vd/spell.vwl.A.fm.pl",
        "vd/long.vwl.harf": "vd/spell.vwl.AYW",
        "vd/long.vwl.noun": "vd/spell.vwl.AYW",
        "vd/long.vwl.prep": "vd/spell.vwl.AYW",
        "vd/long.vwl.pron": "vd/spell.vwl.AYW",
        "vd/long.vwl.verb": "vd/spell.vwl.AYW",
        "vd/long.a.Y-A": "vd/spell.vwl.long.a.A-Y",
        "vd/pass-act": "vd/synt.pass.act",
        "vd/pron.hm.ha": "vd/vwl.h.pron",
        "vd/pron.h.kinaya": "vd/vwl.h.pron",
        "vd/imala": "vd/vwl.imala",
        "vd/int.vwl": "vd/vwl.int",
        "vd/pron.pl.mim.u": "vd/vwl.u.mim.pron",
        "vd/yaat.al.idafa": "vd/vwl.y.pron",
        "vl/harf": "vl/lexicon.harf",
        "vl/haplog": "vl/mech.haplog",
        "vl/long.vwl.dual": "vl/spell.vwl.A.dual",
        "vl/long.vwl.fm.plur": "vl/spell.vwl.A.fm.pl",
        "vl/long.vwl.harf": "vl/spell.vwl.AYW",
        "vl/long.vwl.noun": "vl/spell.vwl.AYW",
        "vl/long.vwl.prep": "vl/spell.vwl.AYW",
        "vl/long.vwl.pron": "vl/spell.vwl.AYW",
        "vl/long.vwl.verb": "vl/spell.vwl.AYW",
        "vl/long.a.Y-A": "vl/spell.vwl.long.a.A-Y",
        "vl/pron.hm.ha": "vl/vwl.h.pron",
        "vl/pron.h.kinaya": "vl/vwl.h.pron",
        "vl/imala": "vl/vwl.imala",
        "vl/int.vwl": "vl/vwl.int",
        "vl/pron.pl.mim.u": "vl/vwl.u.mim.pron",
        "vl/yaat.al.idafa": "vl/vwl.y.pron",
}

REPL_REGEX = re.compile('|'.join(REPL))

if __name__ == '__main__':

    parser = ArgumentParser(description='update new tags in xml transcriptions exported from Archetype')
    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin, help='xml file')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='modified xml file')
    args = parser.parse_args()

    args.outfile.write(REPL_REGEX.sub(lambda m: REPL[m.group(0)], args.infile.read()))

