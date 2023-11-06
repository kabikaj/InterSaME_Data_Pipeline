from digipal.settings_docker import *

# Your custom project settings go here

TEXT_EDITOR_OPTIONS = {
    'buttons': {
        'fasila': {'label': 'fasila', 'xml': '<span data-dpt="divider" data-dpt-type="fasila">{}</span>'},
        'awashir': {'label': 'awashir', 'xml': '<span data-dpt="divider" data-dpt-type="awashir">{}</span>'},
        'khawamis': {'label': 'khawamis', 'xml': '<span data-dpt="divider" data-dpt-type="khawamis">{}</span>'},
        'miaa': {'label': 'miaa', 'xml': '<span data-dpt="divider" data-dpt-type="miaa">{}</span>'},
        'sura': {'label': 'sura', 'xml': '<span data-dpt="divider" data-dpt-type="sura">{}</span>'},
        'ref': {'label': 'ref', 'xml': '<span data-dpt="divider" data-dpt-type="ref">{}</span>'},
        'divider': {'label': 'divider', 'buttons': ['fasila', 'awashir', 'khawamis', 'miaa', 'sura', 'ref']},

        'lacuna': {'label': 'lacuna', 'xml': '<span data-dpt="supplied_" data-dpt-type="lacuna">{}</span>'},
        'unclear': {'label': 'unclear', 'xml': '<span data-dpt="supplied_" data-dpt-type="unclear">{}</span>'},
        'illegible': {'label': 'illegible', 'xml': '<span data-dpt="supplied_" data-dpt-type="illegible">{}</span>'},
        'supplied_': {'label': 'supplied', 'buttons': ['lacuna', 'unclear', 'illegible']},

        'r/alif.al.wasl': {'label': 'r/alif.al.wasl', 'xml': '<span data-dpt="varr" data-dpt-type="r/alif.al.wasl">{}</span>'},
        'r/alif.otiose': {'label': 'r/alif.otiose', 'xml': '<span data-dpt="varr" data-dpt-type="r/alif.otiose">{}</span>'},
        'r/assim': {'label': 'r/assim', 'xml': '<span data-dpt="varr" data-dpt-type="r/assim">{}</span>'},
        'r/hamza': {'label': 'r/hamza', 'xml': '<span data-dpt="varr" data-dpt-type="r/hamza">{}</span>'},
        'r/hamza.two.A': {'label': 'r/hamza.two.A', 'xml': '<span data-dpt="varr" data-dpt-type="r/hamza.two.A">{}</span>'},
        'r/irab': {'label': 'r/irab', 'xml': '<span data-dpt="varr" data-dpt-type="r/irab">{}</span>'},
        'r/layout': {'label': 'r/layout', 'xml': '<span data-dpt="varr" data-dpt-type="r/layout">{}</span>'},
        'r/lexicon': {'label': 'r/lexicon', 'xml': '<span data-dpt="varr" data-dpt-type="r/lexicon">{}</span>'},
        'r/lexicon.harf': {'label': 'r/lexicon.harf', 'xml': '<span data-dpt="varr" data-dpt-type="r/lexicon.harf">{}</span>'},
        'r/lexicon.ibdal': {'label': 'r/lexicon.ibdal', 'xml': '<span data-dpt="varr" data-dpt-type="r/lexicon.ibdal">{}</span>'},
        'r/lexicon.vrb.forms': {'label': 'r/lexicon.vrb.forms', 'xml': '<span data-dpt="varr" data-dpt-type="r/lexicon.vrb.forms">{}</span>'},
        'r/mech': {'label': 'r/mech', 'xml': '<span data-dpt="varr" data-dpt-type="r/mech">{}</span>'},
        'r/mech.haplog': {'label': 'r/mech.haplog', 'xml': '<span data-dpt="varr" data-dpt-type="r/mech.haplog">{}</span>'},
        'r/meta': {'label': 'r/meta', 'xml': '<span data-dpt="varr" data-dpt-type="r/meta">{}</span>'},
        'r/script': {'label': 'r/script', 'xml': '<span data-dpt="varr" data-dpt-type="r/script">{}</span>'},
        'r/spell.ta.marb': {'label': 'r/spell.ta.marb', 'xml': '<span data-dpt="varr" data-dpt-type="r/spell.ta.marb">{}</span>'},
        'r/spell.vwl.A.dual': {'label': 'r/spell.vwl.A.dual', 'xml': '<span data-dpt="varr" data-dpt-type="r/spell.vwl.A.dual">{}</span>'},
        'r/spell.vwl.A.fm.pl': {'label': 'r/spell.vwl.A.fm.pl', 'xml': '<span data-dpt="varr" data-dpt-type="r/spell.vwl.A.fm.pl">{}</span>'},
        'r/spell.vwl.AYW': {'label': 'r/spell.vwl.AYW', 'xml': '<span data-dpt="varr" data-dpt-type="r/spell.vwl.AYW">{}</span>'},
        'r/spell.vwl.long.a.A-Y': {'label': 'r/spell.vwl.long.a.A-Y', 'xml': '<span data-dpt="varr" data-dpt-type="r/spell.vwl.long.a.A-Y">{}</span>'},
        'r/synt.agreem': {'label': 'r/synt.agreem', 'xml': '<span data-dpt="varr" data-dpt-type="r/synt.agreem">{}</span>'},
        'r/synt.pass.act': {'label': 'r/synt.pass.act', 'xml': '<span data-dpt="varr" data-dpt-type="r/synt.pass.act">{}</span>'},
        'r/synt.pron': {'label': 'r/synt.pron', 'xml': '<span data-dpt="varr" data-dpt-type="r/synt.pron">{}</span>'},
        'r/synt.sg.pl.dual': {'label': 'r/synt.sg.pl.dual', 'xml': '<span data-dpt="varr" data-dpt-type="r/synt.sg.pl.dual">{}</span>'},
        'r/synt.verb.tense': {'label': 'r/synt.verb.tense', 'xml': '<span data-dpt="varr" data-dpt-type="r/synt.verb.tense">{}</span>'},
        'r/syntax': {'label': 'r/syntax', 'xml': '<span data-dpt="varr" data-dpt-type="r/syntax">{}</span>'},
        'r/tanwin': {'label': 'r/tanwin', 'xml': '<span data-dpt="varr" data-dpt-type="r/tanwin">{}</span>'},
        'r/unclass': {'label': 'r/unclass', 'xml': '<span data-dpt="varr" data-dpt-type="r/unclass">{}</span>'},
        'r/unknown': {'label': 'r/unknown', 'xml': '<span data-dpt="varr" data-dpt-type="r/unknown">{}</span>'},
        'r/vrb.morpho': {'label': 'r/vrb.morpho', 'xml': '<span data-dpt="varr" data-dpt-type="r/vrb.morpho">{}</span>'},
        'r/vwl.h.pron': {'label': 'r/vwl.h.pron', 'xml': '<span data-dpt="varr" data-dpt-type="r/vwl.h.pron">{}</span>'},
        'r/vwl.imala': {'label': 'r/vwl.imala', 'xml': '<span data-dpt="varr" data-dpt-type="r/vwl.imala">{}</span>'},
        'r/vwl.u.mim.pron': {'label': 'r/vwl.u.mim.pron', 'xml': '<span data-dpt="varr" data-dpt-type="r/vwl.u.mim.pron">{}</span>'},
        'r/vwl.y.pron': {'label': 'r/vwl.y.pron', 'xml': '<span data-dpt="varr" data-dpt-type="r/vwl.y.pron">{}</span>'},
        'varr': {'label': 'variant.r', 'buttons': ['r/alif.al.wasl', 'r/alif.otiose', 'r/assim', 'r/hamza', 'r/hamza.two.A', 'r/irab', 'r/layout', 'r/lexicon', 'r/lexicon.harf', 'r/lexicon.ibdal', 'r/lexicon.vrb.forms', 'r/mech', 'r/mech.haplog', 'r/meta', 'r/script', 'r/spell.ta.marb', 'r/spell.vwl.A.dual', 'r/spell.vwl.A.fm.pl', 'r/spell.vwl.AYW', 'r/spell.vwl.long.a.A-Y', 'r/synt.agreem', 'r/synt.pass.act', 'r/synt.pron', 'r/synt.sg.pl.dual', 'r/synt.verb.tense', 'r/syntax', 'r/tanwin', 'r/unclass', 'r/unknown', 'r/vrb.morpho', 'r/vwl.h.pron', 'r/vwl.imala', 'r/vwl.u.mim.pron', 'r/vwl.y.pron']},

        'cd/assim': {'label': 'cd/assim', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/assim">{}</span>'},
        'cd/hamza': {'label': 'cd/hamza', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/hamza">{}</span>'},
        'cd/irab': {'label': 'cd/irab', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/irab">{}</span>'},
        'cd/layout': {'label': 'cd/layout', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/layout">{}</span>'},
        'cd/lexicon': {'label': 'cd/lexicon', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/lexicon">{}</span>'},
        'cd/lexicon.harf': {'label': 'cd/lexicon.harf', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/lexicon.harf">{}</span>'},
        'cd/lexicon.ibdal': {'label': 'cd/lexicon.ibdal', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/lexicon.ibdal">{}</span>'},
        'cd/lexicon.vrb.forms': {'label': 'cd/lexicon.vrb.forms', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/lexicon.vrb.forms">{}</span>'},
        'cd/mech': {'label': 'cd/mech', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/mech">{}</span>'},
        'cd/mech.haplog': {'label': 'cd/mech.haplog', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/mech.haplog">{}</span>'},
        'cd/meta': {'label': 'cd/meta', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/meta">{}</span>'},
        'cd/script': {'label': 'cd/script', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/script">{}</span>'},
        'cd/spell.ta.marb': {'label': 'cd/spell.ta.marb', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/spell.ta.marb">{}</span>'},
        'cd/spell.vwl.A.dual': {'label': 'cd/spell.vwl.A.dual', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/spell.vwl.A.dual">{}</span>'},
        'cd/spell.vwl.AYW': {'label': 'cd/spell.vwl.AYW', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/spell.vwl.AYW">{}</span>'},
        'cd/spell.vwl.long.a.A-Y': {'label': 'cd/spell.vwl.long.a.A-Y', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/spell.vwl.long.a.A-Y">{}</span>'},
        'cd/synt.agreem': {'label': 'cd/synt.agreem', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/synt.agreem">{}</span>'},
        'cd/synt.pass.act': {'label': 'cd/synt.pass.act', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/synt.pass.act">{}</span>'},
        'cd/synt.pron': {'label': 'cd/synt.pron', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/synt.pron">{}</span>'},
        'cd/synt.sg.pl.dual': {'label': 'cd/synt.sg.pl.dual', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/synt.sg.pl.dual">{}</span>'},
        'cd/synt.verb.tense': {'label': 'cd/synt.verb.tense', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/synt.verb.tense">{}</span>'},
        'cd/syntax': {'label': 'cd/syntax', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/syntax">{}</span>'},
        'cd/unclass': {'label': 'cd/unclass', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/unclass">{}</span>'},
        'cd/unclass.LA': {'label': 'cd/unclass.LA', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/unclass.LA">{}</span>'},
        'cd/unknown': {'label': 'cd/unknown', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/unknown">{}</span>'},
        'cd/vrb.morpho': {'label': 'cd/vrb.morpho', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/vrb.morpho">{}</span>'},
        'cd/vwl.y.pron': {'label': 'cd/vwl.y.pron', 'xml': '<span data-dpt="varcd" data-dpt-type="cd/vwl.y.pron">{}</span>'},
        'varcd': {'label': 'variant.cd', 'buttons': ['cd/assim', 'cd/hamza', 'cd/irab', 'cd/layout', 'cd/lexicon', 'cd/lexicon.harf', 'cd/lexicon.ibdal', 'cd/lexicon.vrb.forms', 'cd/mech', 'cd/mech.haplog', 'cd/meta', 'cd/script', 'cd/spell.ta.marb', 'cd/spell.vwl.A.dual', 'cd/spell.vwl.AYW', 'cd/spell.vwl.long.a.A-Y', 'cd/synt.agreem', 'cd/synt.pass.act', 'cd/synt.pron', 'cd/synt.sg.pl.dual', 'cd/synt.verb.tense', 'cd/syntax', 'cd/unclass', 'cd/unclass.LA', 'cd/unknown', 'cd/vrb.morpho', 'cd/vwl.y.pron']},

        'vd/alif.al.wasl': {'label': 'vd/alif.al.wasl', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/alif.al.wasl">{}</span>'},
        'vd/alif.otiose': {'label': 'vd/alif.otiose', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/alif.otiose">{}</span>'},
        'vd/assim': {'label': 'vd/assim', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/assim">{}</span>'},
        'vd/hamza': {'label': 'vd/hamza', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/hamza">{}</span>'},
        'vd/hamza.two.A': {'label': 'vd/hamza.two.A', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/hamza.two.A">{}</span>'},
        'vd/irab': {'label': 'vd/irab', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/irab">{}</span>'},
        'vd/layout': {'label': 'vd/layout', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/layout">{}</span>'},
        'vd/lexicon': {'label': 'vd/lexicon', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/lexicon">{}</span>'},
        'vd/lexicon.harf': {'label': 'vd/lexicon.harf', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/lexicon.harf">{}</span>'},
        'vd/lexicon.vrb.forms': {'label': 'vd/lexicon.vrb.forms', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/lexicon.vrb.forms">{}</span>'},
        'vd/mech': {'label': 'vd/mech', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/mech">{}</span>'},
        'vd/mech.haplog': {'label': 'vd/mech.haplog', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/mech.haplog">{}</span>'},
        'vd/meta': {'label': 'vd/meta', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/meta">{}</span>'},
        'vd/posit': {'label': 'vd/posit', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/posit">{}</span>'},
        'vd/script': {'label': 'vd/script', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/script">{}</span>'},
        'vd/spell.vwl.A.dual': {'label': 'vd/spell.vwl.A.dual', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/spell.vwl.A.dual">{}</span>'},
        'vd/spell.vwl.A.fm.pl': {'label': 'vd/spell.vwl.A.fm.pl', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/spell.vwl.A.fm.pl">{}</span>'},
        'vd/spell.vwl.AYW': {'label': 'vd/spell.vwl.AYW', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/spell.vwl.AYW">{}</span>'},
        'vd/spell.vwl.long.a.A-Y': {'label': 'vd/spell.vwl.long.a.A-Y', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/spell.vwl.long.a.A-Y">{}</span>'},
        'vd/synt.sg.pl.dual': {'label': 'vd/synt.sg.pl.dual', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/synt.sg.pl.dual">{}</span>'},
        'vd/synt.agreem': {'label': 'vd/synt.agreem', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/synt.agreem">{}</span>'},
        'vd/synt.pass.act': {'label': 'vd/synt.pass.act', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/synt.pass.act">{}</span>'},
        'vd/synt.pron': {'label': 'vd/synt.pron', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/synt.pron">{}</span>'},
        'vd/synt.verb.tense': {'label': 'vd/synt.verb.tense', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/synt.verb.tense">{}</span>'},
        'vd/syntax': {'label': 'vd/syntax', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/syntax">{}</span>'},
        'vd/tanwin': {'label': 'vd/tanwin', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/tanwin">{}</span>'},
        'vd/unclass': {'label': 'vd/unclass', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/unclass">{}</span>'},
        'vd/unknown': {'label': 'vd/unknown', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/unknown">{}</span>'},
        'vd/vrb.morpho': {'label': 'vd/vrb.morpho', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/vrb.morpho">{}</span>'},
        'vd/vwl.h.pron': {'label': 'vd/vwl.h.pron', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/vwl.h.pron">{}</span>'},
        'vd/vwl.imala': {'label': 'vd/vwl.imala', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/vwl.imala">{}</span>'},
        'vd/vwl.int': {'label': 'vd/vwl.int', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/vwl.int">{}</span>'},
        'vd/vwl.taskin.L': {'label': 'vd/vwl.taskin.L', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/vwl.taskin.L">{}</span>'},
        'vd/vwl.u.mim.pron': {'label': 'vd/vwl.u.mim.pron', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/vwl.u.mim.pron">{}</span>'},
        'vd/vwl.y.pron': {'label': 'vd/vwl.y.pron', 'xml': '<span data-dpt="varvd" data-dpt-type="vd/vwl.y.pron">{}</span>'},
        'varvd': {'label': 'variant.vd', 'buttons': ['vd/alif.al.wasl', 'vd/alif.otiose', 'vd/assim', 'vd/hamza', 'vd/hamza.two.A', 'vd/irab', 'vd/layout', 'vd/lexicon', 'vd/lexicon.harf', 'vd/lexicon.vrb.forms', 'vd/mech', 'vd/mech.haplog', 'vd/meta', 'vd/posit', 'vd/script', 'vd/spell.vwl.A.dual', 'vd/spell.vwl.A.fm.pl', 'vd/spell.vwl.AYW', 'vd/spell.vwl.long.a.A-Y', 'vd/synt.sg.pl.dual', 'vd/synt.agreem', 'vd/synt.pass.act', 'vd/synt.pron', 'vd/synt.verb.tense', 'vd/syntax', 'vd/tanwin', 'vd/unclass', 'vd/unknown', 'vd/vrb.morpho', 'vd/vwl.h.pron', 'vd/vwl.imala', 'vd/vwl.int', 'vd/vwl.taskin.L', 'vd/vwl.u.mim.pron', 'vd/vwl.y.pron']},
        
        'vl/alif.al.wasl': {'label': 'vl/alif.al.wasl', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/alif.al.wasl">{}</span>'},
        'vl/alif.otiose': {'label': 'vl/alif.otiose', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/alif.otiose">{}</span>'},
        'vl/assim': {'label': 'vl/assim', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/assim">{}</span>'},
        'vl/hamza': {'label': 'vl/hamza', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/hamza">{}</span>'},
        'vl/hamza.two.A': {'label': 'vl/hamza.two.A', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/hamza.two.A">{}</span>'},
        'vl/irab': {'label': 'vl/irab', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/irab">{}</span>'},
        'vl/layout': {'label': 'vl/layout', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/layout">{}</span>'},
        'vl/lexicon': {'label': 'vl/lexicon', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/lexicon">{}</span>'},
        'vl/lexicon.harf': {'label': 'vl/lexicon.harf', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/lexicon.harf">{}</span>'},
        'vl/lexicon.vrb.forms': {'label': 'vl/lexicon.vrb.forms', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/lexicon.vrb.forms">{}</span>'},
        'vl/mech': {'label': 'vl/mech', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/mech">{}</span>'},
        'vl/mech.haplog': {'label': 'vl/mech.haplog', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/mech.haplog">{}</span>'},
        'vl/meta': {'label': 'vl/meta', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/meta">{}</span>'},
        'vl/posit': {'label': 'vl/posit', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/posit">{}</span>'},
        'vl/script': {'label': 'vl/script', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/script">{}</span>'},
        'vl/spell.vwl.A.dual': {'label': 'vl/spell.vwl.A.dual', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/spell.vwl.A.dual">{}</span>'},
        'vl/spell.vwl.A.fm.pl': {'label': 'vl/spell.vwl.A.fm.pl', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/spell.vwl.A.fm.pl">{}</span>'},
        'vl/spell.vwl.AYW': {'label': 'vl/spell.vwl.AYW', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/spell.vwl.AYW">{}</span>'},
        'vl/spell.vwl.long.a.A-Y': {'label': 'vl/spell.vwl.long.a.A-Y', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/spell.vwl.long.a.A-Y">{}</span>'},
        'vl/synt.sg.pl.dual': {'label': 'vl/synt.sg.pl.dual', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/synt.sg.pl.dual">{}</span>'},
        'vl/synt.agreem': {'label': 'vl/synt.agreem', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/synt.agreem">{}</span>'},
        'vl/synt.pass.act': {'label': 'vl/synt.pass.act', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/synt.pass.act">{}</span>'},
        'vl/synt.pron': {'label': 'vl/synt.pron', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/synt.pron">{}</span>'},
        'vl/synt.verb.tense': {'label': 'vl/synt.verb.tense', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/synt.verb.tense">{}</span>'},
        'vl/syntax': {'label': 'vl/syntax', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/syntax">{}</span>'},
        'vl/tanwin': {'label': 'vl/tanwin', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/tanwin">{}</span>'},
        'vl/unclass': {'label': 'vl/unclass', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/unclass">{}</span>'},
        'vl/unknown': {'label': 'vl/unknown', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/unknown">{}</span>'},
        'vl/vrb.morpho': {'label': 'vl/vrb.morpho', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/vrb.morpho">{}</span>'},
        'vl/vwl.h.pron': {'label': 'vl/vwl.h.pron', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/vwl.h.pron">{}</span>'},
        'vl/vwl.imala': {'label': 'vl/vwl.imala', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/vwl.imala">{}</span>'},        
        'vl/vwl.int': {'label': 'vl/vwl.int', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/vwl.int">{}</span>'},
        'vl/vwl.taskin.L': {'label': 'vl/vwl.taskin.L', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/vwl.taskin.L">{}</span>'},
        'vl/vwl.u.mim.pron': {'label': 'vl/vwl.u.mim.pron', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/vwl.u.mim.pron">{}</span>'},
        'vl/vwl.y.pron': {'label': 'vl/vwl.y.pron', 'xml': '<span data-dpt="varvl" data-dpt-type="vl/vwl.y.pron">{}</span>'},
        'varvl': {'label': 'variant.vl', 'buttons': ['vl/alif.al.wasl', 'vl/alif.otiose', 'vl/assim', 'vl/hamza', 'vl/hamza.two.A', 'vl/irab', 'vl/layout', 'vl/lexicon', 'vl/lexicon.harf', 'vl/lexicon.vrb.forms', 'vl/mech', 'vl/mech.haplog', 'vl/meta', 'vl/posit', 'vl/script', 'vl/spell.vwl.A.dual', 'vl/spell.vwl.A.fm.pl', 'vl/spell.vwl.AYW', 'vl/spell.vwl.long.a.A-Y', 'vl/synt.sg.pl.dual', 'vl/synt.agreem', 'vl/synt.pass.act', 'vl/synt.pron', 'vl/synt.verb.tense', 'vl/syntax', 'vl/tanwin', 'vl/unclass', 'vl/unknown', 'vl/vrb.morpho', 'vl/vwl.h.pron', 'vl/vwl.imala', 'vl/vwl.int', 'vl/vwl.taskin.L', 'vl/vwl.u.mim.pron', 'vl/vwl.y.pron']},

        'sub/basmala': {'label': 'sub/basmala', 'xml': '<span data-dpt="varsub" data-dpt-type="sub/basmala">{}</span>'},
        'sub/fasila': {'label': 'sub/fasila', 'xml': '<span data-dpt="varsub" data-dpt-type="sub/fasila">{}</span>'},
        'sub/awashir': {'label': 'sub/awashir', 'xml': '<span data-dpt="varsub" data-dpt-type="sub/awashir">{}</span>'},
        'sub/khawamis': {'label': 'sub/khawamis', 'xml': '<span data-dpt="varsub" data-dpt-type="sub/khawamis">{}</span>'},
        'sub/miaa': {'label': 'sub/miaa', 'xml': '<span data-dpt="varsub" data-dpt-type="sub/miaa">{}</span>'},
        'sub/words': {'label': 'sub/words', 'xml': '<span data-dpt="varsub" data-dpt-type="sub/words">{}</span>'},
        'sub/no.verses': {'label': 'sub/no.verses', 'xml': '<span data-dpt="varsub" data-dpt-type="sub/no.verses">{}</span>'},
        'sub/unclass': {'label': 'sub/unclass', 'xml': '<span data-dpt="varsub" data-dpt-type="sub/unclass">{}</span>'},
        'varsub': {'label': 'variant.sub', 'buttons': ['sub/basmala', 'sub/fasila', 'sub/awashir', 'sub/khawamis', 'sub/miaa', 'sub/words', 'sub/no.verses', 'sub/unclass']},

        'n.dots': {'label': 'n.dots', 'xml': '<span data-dpt="note_" data-dpt-type="n.dots">{}</span>'},
        'n.layers': {'label': 'n.layers', 'xml': '<span data-dpt="note_" data-dpt-type="n.layers">{}</span>'},
        'n.palaeog': {'label': 'n.palaeog', 'xml': '<span data-dpt="note_" data-dpt-type="n.palaeog">{}</span>'},
        'n.reading': {'label': 'n.reading', 'xml': '<span data-dpt="note_" data-dpt-type="n.reading">{}</span>'},
        'n.codic': {'label': 'n.codic', 'xml': '<span data-dpt="note_" data-dpt-type="n.codic">{}</span>'},
        'n.ortho': {'label': 'n.ortho', 'xml': '<span data-dpt="note_" data-dpt-type="n.ortho">{}</span>'},
        'note_': {'label': 'note', 'buttons': ['n.dots', 'n.layers', 'n.palaeog', 'n.reading', 'n.codic', 'n.ortho']},
    },
    'toolbars': {
        'default': 'psclear undo redo code | psconvert | pslocation | divider | supplied_ | varr | varcd | varvd | varvl | varsub | note_',
        'translation': 'psclear undo redo code | pslocation | divider',
    },
    'panels': {
        'north': {
            'ratio': 0.6
        },
        'east': {
            'ratio': 0.5
        },
    }
}
