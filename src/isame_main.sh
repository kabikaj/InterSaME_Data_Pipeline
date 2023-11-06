#!bin/bash
#
#    isame_main.sh
#
# processing workflow of intersame transcriptions
#
# this script is not to be executed all at once, but it's supposed to serve as repo 
# for all the pieces of code necessary to process each manuscript fragment.
# The processing is delicate, so it's better to check slowly each step. 
#
####################################################################################

RED='\033[0;31m'
RESET='\033[0m'

printf "${RED}Do not execute this main directly! "
printf "Just copy paste in the terminal the processing pipeline of each fragment individualy${RESET}\n"

exit 0

####################################
# F001 - BnF.Ar.330f and OIC.A6961-1
####################################

#
# process only fragment BnF.Ar.330f
#

python isame_xml2txt.py -f ../../data/arabic/trans/F001_BnF.Ar.330f-3-trans.xml |
  tee ../../data/arabic/trans/F001_BnF.Ar.330f-4.txt | python isame_parser.py |
  tee ../../data/arabic/trans/F001_BnF.Ar.330f-5-pre.json | python isame_mapper.py |
  tee ../../data/arabic/trans/F001_BnF.Ar.330f-6.json | python isame_json2tei.py > ../../data/arabic/trans/F001_BnF.Ar.330f-7.xml
cat ../../data/arabic/trans/F001-6.json | python isame_json2tei.py --ara --sep " " > ../../data/arabic/trans/F001-7-ara.xml
cat ../../data/arabic/trans/F001_BnF.Ar.330f-6.json | python isame_json2csv.py > ../../data/arabic/trans/F001_BnF.Ar.330f-7.csv

xmllint --relaxng tei_all.rng ../../data/arabic/trans/F001_BnF.Ar.330f-7.xml --noout

# -> testing for changes in code
diff <(python isame_xml2txt.py -f ../../data/arabic/trans/F001_BnF.Ar.330f-3-trans.xml | python isame_parser.py | python isame_mapper.py | python isame_json2tei.py) ../../data/arabic/trans/F001_BnF.Ar.330f-7.xml

#
# process only fragment OIC.A6961
#

cat ../../data/arabic/trans/F001_OIC.A6961-1-ini.txt | python isame_prepare.py --qaf_above --fa_below --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F001_OIC.A6961-2-draft-pl.txt --out_ara ../../data/arabic/trans/F001_OIC.A6961-2-draft-ar.txt

python isame_xml2txt.py -f ../../data/arabic/trans/F001_OIC.A6961-3-trans.xml |
  tee ../../data/arabic/trans/F001_OIC.A6961-4.txt | python isame_parser.py |
  tee ../../data/arabic/trans/F001_OIC.A6961-5-pre.json | python isame_mapper.py |
  tee ../../data/arabic/trans/F001_OIC.A6961-6.json | python isame_json2tei.py > ../../data/arabic/trans/F001_OIC.A6961-7.xml
cat ../../data/arabic/trans/F001_OIC.A6961-6.json | python isame_json2tei.py --ara --sep " " > ../../data/arabic/trans/F001_OIC.A6961-7.ara.xml
cat ../../data/arabic/trans/F001_OIC.A6961-6.json | python isame_json2csv.py > ../../data/arabic/trans/F001_OIC.A6961-7.csv

xmllint --relaxng tei_all.rng ../../data/arabic/trans/F001_OIC.A6961-7.xml --noout

# -> testing for changes in code
diff <(python isame_xml2txt.py -f ../../data/arabic/trans/F001_OIC.A6961-3-trans.xml | python isame_parser.py | python isame_mapper.py | python isame_json2tei.py) ../../data/arabic/trans/F001_OIC.A6961-7.xml

#
# process complete F001 (for now only BnF.Ar.330f and OIC.A6961-1)
#

python isame_xml2txt.py -f ../../data/arabic/trans/F001_BnF.Ar.330f-3-trans.xml ../../data/arabic/trans/F001_OIC.A6961-3-trans.xml |
  tee ../../data/arabic/trans/F001-4.txt | python isame_parser.py |
  tee ../../data/arabic/trans/F001-5-pre.json | python isame_mapper.py |
  tee ../../data/arabic/trans/F001-6.json | python isame_json2tei.py > ../../data/arabic/trans/F001-7.xml
cat ../../data/arabic/trans/F001-6.json | python isame_json2tei.py --ara --sep " " > ../../data/arabic/trans/F001-7-ara.xml
cat ../../data/arabic/trans/F001-6.json | python isame_json2csv.py > ../../data/arabic/trans/F001-7.csv

xmllint --relaxng tei_all.rng ../../data/arabic/trans/F001-7-ara.xml --noout

# -> testing for changes in code
diff <(python isame_xml2txt.py -f ../../data/arabic/trans/F001_BnF.Ar.330f-3-trans.xml ../../data/arabic/trans/F001_OIC.A6961-3-trans.xml | python isame_parser.py | python isame_mapper.py | python isame_json2tei.py) ../../data/arabic/trans/F001-7.xml

###################
# F002 - BnF.Ar.327
###################

cat ../../data/arabic/trans/F002_BnF.Ar.327-1-ini.txt | python isame_prepare.py --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F002_BnF.Ar.327-2-draft-pl.txt --out_ara ../../data/arabic/trans/F002_BnF.Ar.327-2-draft-ar.txt

python isame_xml2txt.py -f ../../data/arabic/trans/F002_BnF.Ar.327-3-trans.xml |
  tee ../../data/arabic/trans/F002_BnF.Ar.327-4.txt | python isame_parser.py |
  tee ../../data/arabic/trans/F002_BnF.Ar.327-5-pre.json | python isame_mapper.py |
  tee ../../data/arabic/trans/F002_BnF.Ar.327-6.json | python isame_json2tei.py > ../../data/arabic/trans/F002_BnF.Ar.327-7.xml
cat ../../data/arabic/trans/F002_BnF.Ar.327-6.json | python isame_json2tei.py --ara --sep " " > ../../data/arabic/trans/F002_BnF.Ar.327-7-ara.xml
cat ../../data/arabic/trans/F002_BnF.Ar.327-6.json | python isame_json2csv.py > ../../data/arabic/trans/F002_BnF.Ar.327-7.csv

xmllint --relaxng tei_all.rng ../../data/arabic/trans/F002_BnF.Ar.327-7.xml --noout

###################
# F003 - BnF.Ar.330b
###################

cat ../../data/arabic/trans/F003_BnF.Ar.330b-1-ini.txt | python isame_prepare.py --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F003_BnF.Ar.330b-2-draft-pl.txt --out_ara ../../data/arabic/trans/F003_BnF.Ar.330b-2-draft-ar.txt

python isame_xml2txt.py -f ../../data/arabic/trans/F003_BnF.Ar.330b-3-trans.xml |
  tee ../../data/arabic/trans/F003_BnF.Ar.330b-4.txt | python isame_parser.py |
  tee ../../data/arabic/trans/F003_BnF.Ar.330b-5-pre.json | python isame_mapper.py |
  tee ../../data/arabic/trans/F003_BnF.Ar.330b-6.json | python isame_json2tei.py > ../../data/arabic/trans/F003_BnF.Ar.330b-7.xml
cat ../../data/arabic/trans/F003_BnF.Ar.330b-6.json | python isame_json2tei.py --ara --sep " " > ../../data/arabic/trans/F003_BnF.Ar.330b-7-ara.xml
cat ../../data/arabic/trans/F003_BnF.Ar.330b-6.json | python isame_json2csv.py > ../../data/arabic/trans/F003_BnF.Ar.330b-7.csv

xmllint --relaxng tei_all.rng ../../data/arabic/trans/F003_BnF.Ar.330b-7.xml --noout

######################
# F005 - BnF.Ar.329c - transcribed by Laura but no variants
######################


######################
# F007 - BnF.Ar.330d - 
######################

cat ../../data/arabic/trans/F007_BnF.Ar.330d-1-ini.txt |
  python isame_prepare.py --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F007_BnF.Ar.330d-2-draft-pl.txt --out_ara ../../data/arabic/trans/F007_BnF.Ar.330d-2-draft-ar.txt

######################
# F011 - BnF.Ar.334h - 68-87 (processed only 68-69)
######################

python isame_get_text.py -i 4:19:31-4:30:10 | xclip -selection clipboard

cat ../../data/arabic/trans/F011_BnF.Ar.334h-1-ini.txt |
  python isame_prepare.py --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F011_BnF.Ar.334h-2-draft-pl.txt --out_ara ../../data/arabic/trans/F011_BnF.Ar.334h-2-draft-ar.txt

######################
# F012 - BnF.Ar.338a - 1-12
######################

python isame_get_text.py -i 40:3:2-44:40:4 | xclip -selection clipboard
python isame_get_text.py -i 42:15:23-42:21:17 | xclip -selection clipboard
python isame_get_text.py -i 44:7:3-44:40:4 | xclip -selection clipboard

cat ../../data/arabic/trans/F012_BnF.Ar.338a-1-ini.txt |
  python isame_prepare.py --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F012_BnF.Ar.338a-2-draft-pl.txt --out_ara ../../data/arabic/trans/F012_BnF.Ar.338a-2-draft-ar.txt

######################
# F013 - BnF.Ar.338b - 13r, 13v, 14r, 14v
######################

python isame_get_text.py -i 4:141:25-5:1:1 | xclip -selection clipboard

cat ../../data/arabic/trans/F013_BnF.Ar.338b-1-ini.txt |
  python isame_prepare.py --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F013_BnF.Ar.338b-2-draft-pl.txt --out_ara ../../data/arabic/trans/F013_BnF.Ar.338b-2-draft-ar.txt

######################
# F014 - BnF.Ar.338c - 36r, 36v, 37r, 37v
######################

python isame_get_text.py -i 4:95:17-4:105:9 | xclip -selection clipboard

cat ../../data/arabic/trans/F014_BnF.Ar.338c-1-ini.txt |
  python isame_prepare.py --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F014_BnF.Ar.338c-2-draft-pl.txt --out_ara ../../data/arabic/trans/F014_BnF.Ar.338c-2-draft-ar.txt

python isame_xml2txt.py -f ../../data/arabic/trans/F014_BnF.Ar.338c-3-trans.xml | 
  tee ../../data/arabic/trans/F014_BnF.Ar.338c-4.txt | python isame_parser.py | 
  tee ../../data/arabic/trans/F014_BnF.Ar.338c-5-pre.json | python isame_mapper.py |
  tee ../../data/arabic/trans/F014_BnF.Ar.338c-6.json | python isame_json2tei.py > ../../data/arabic/trans/F014_BnF.Ar.338c-7.xml
cat ../../data/arabic/trans/F014_BnF.Ar.338c-6.json | python isame_json2csv.py > ../../data/arabic/trans/F014_BnF.Ar.338c.csv

cat ../../data/arabic/trans/F014_BnF.Ar.338c-6.json | python isame_json2tei.py --ara --sep " " > ../../data/arabic/trans/F014_BnF.Ar.338c-7-ara.xml

xmllint --relaxng tei_all.rng ../../data/arabic/trans/F014_BnF.Ar.338c-7.xml --noout
xmllint --relaxng tei_all.rng ../../data/arabic/trans/F014_BnF.Ar.338c-7-ara.xml --noout

######################
# F015 - BnF.Ar.340c - 31r, 31v, 32r, 32v
######################

python isame_get_text.py -i 13:14:20-14:1:1 | xclip -selection clipboard

cat ../../data/arabic/trans/F015_BnF.Ar.340c-1-ini.txt |
  python isame_prepare.py --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F015_BnF.Ar.340c-2-draft-pl.txt --out_ara ../../data/arabic/trans/F015_BnF.Ar.340c-2-draft-ar.txt

######################
# F016 - BnF.Ar.340d - 47r, 47v, 48r, 48v
######################

python isame_get_text.py -i 9:118:14-11:85:12 | xclip -selection clipboard

cat ../../data/arabic/trans/F016_BnF.Ar.340d-1-ini.txt |
  python isame_prepare.py --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F016_BnF.Ar.340d-2-draft-pl.txt --out_ara ../../data/arabic/trans/F016_BnF.Ar.340d-2-draft-ar.txt

######################
# F017 - BnF.Ar.340f - daniela
######################

python isame_get_text.py -i 3:103:33-3:114:15 | xclip -selection clipboard
python isame_get_text.py -i 3:159:19-3:181:21 | xclip -selection clipboard
python isame_get_text.py -i 7:27:9-7:151:1 | xclip -selection clipboard
python isame_get_text.py -i 39:7:29-40:67:19 | xclip -selection clipboard
python isame_get_text.py -i 45:28:1-46:3:9 | xclip -selection clipboard
python isame_get_text.py -i 53:29:11-54:27:7 | xclip -selection clipboard

cat ../../data/arabic/trans/F017_BnF.Ar.340f-1-ini.txt | python isame_prepare.py --ya_tail_marks --G_tail_marks --rm_cons_stokes \
    --out_pal ../../data/arabic/trans/F017_BnF.Ar.340f-2-draft-pl.txt --out_ara ../../data/arabic/trans/F017_BnF.Ar.340f-2-draft-ar.txt

######################
# F018 - BnF.Ar.340i - 120r, 120v, 121r, 121v
######################

python isame_get_text.py -i 48:4:19-48:20:1 | xclip -selection clipboard

cat ../../data/arabic/trans/F018_BnF.Ar.340i-1-ini.txt |
  python isame_prepare.py --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F018_BnF.Ar.340i-2-draft-pl.txt --out_ara ../../data/arabic/trans/F018_BnF.Ar.340i-2-draft-ar.txt

######################
# F019 - BnF.Ar.349f - 119r, 119v, 120r, 120v
######################

python isame_get_text.py -i 9:74:15-10:1:1 | xclip -selection clipboard

cat ../../data/arabic/trans/F019_BnF.Ar.349f-1-ini.txt |
  python isame_prepare.py --ya_tail_marks --G_tail_marks \
  --out_pal ../../data/arabic/trans/F019_BnF.Ar.349f-2-draft-pl.txt --out_ara ../../data/arabic/trans/F019_BnF.Ar.349f-2-draft-ar.txt

######################
# D001  transcribed until 17r (inclusive)
######################

cat ../../data/arabic/trans/D001_UbT.Ma.VI.165-1-ini.txt | python isame_prepare.py --rm_cons_final_ya --ya_tail_marks --G_tail_marks --rm_cons_fa_qaf \
    --out_pal ../../data/arabic/trans/D001_UbT.Ma.VI.165-2-draft-pl.txt --out_ara ../../data/arabic/trans/D001_UbT.Ma.VI.165-2-draft-ar.txt

python isame_xml2txt.py -f ../../data/arabic/trans/D001_UbT.Ma.VI.165-3-trans.xml |
  tee ../../data/arabic/trans/D001_UbT.Ma.VI.165-4.txt | python isame_parser.py | 
  tee ../../data/arabic/trans/D001_UbT.Ma.VI.165-5-pre.json | python isame_mapper.py |
  tee ../../data/arabic/trans/D001_UbT.Ma.VI.165-6.json | python isame_json2tei.py > ../../data/arabic/trans/D001_UbT.Ma.VI.165-7.xml
cat ../../data/arabic/trans/D001_UbT.Ma.VI.165-6.json | python isame_json2csv.py > ../../data/arabic/trans/D001_UbT.Ma.VI.165.csv

xmllint --relaxng tei_all.rng ../../data/arabic/trans/D001_UbT.Ma.VI.165-7.xml --noout

#DEBUG =================================================== #DEBUG
cat test.txt | python isame_parser.py
cat ../../data/arabic/trans/F014_BnF.Ar.338c-4.txt | python isame_parser.py | tee ../../data/arabic/trans/F014_BnF.Ar.338c-5-pre.json |python isame_mapper.py | \
  tee ../../data/arabic/trans/F014_BnF.Ar.338c-6.json | python isame_json2tei.py > ../../data/arabic/trans/F014_BnF.Ar.338c-7.xml
#DEBUG =================================================== #DEBUG

##########################################################################################################################################
#
# CREATE COMPLETE CSV FILE
#

awk 'FNR==1 && NR!=1{next;}{print}' ../../data/arabic/trans/F001-7.csv \
                                    ../../data/arabic/trans/D001_UbT.Ma.VI.165.csv \
                                    ../../data/arabic/trans/F014_BnF.Ar.338c.csv > ../../../github/InterSaME/data/tabular/InterSaME.csv

#awk 'FNR==1 && NR!=1{next;}{print}' ../../data/arabic/trans/F001_BnF.Ar.330f-7.csv \
#                                    ../../data/arabic/trans/F001_OIC.A6961-7.csv \
#                                    ../../data/arabic/trans/D001_UbT.Ma.VI.165.csv \
#                                    ../../data/arabic/trans/F014_BnF.Ar.338c.csv > ../../../github/InterSaME/data/tabular/InterSaME.csv

#awk 'FNR==1 && NR!=1{next;}{print}'  ../../data/arabic/trans/F001_OIC.A6961-7.csv ../../data/arabic/trans/D001_UbT.Ma.VI.165.csv \
#    ../../data/arabic/trans/F014_BnF.Ar.338c.csv > ../../../github/InterSaME/data/tabular/InterSaME_analysis.csv


# EXCHANGE
cat ../../data/arabic/exchange/D014_CUL_Add.1116-4-alba.txt | python isame_parser.py | tee ../../data/arabic/exchange/D014_CUL_Add.1116-5-pre-a2.json | python isame_mapper.py
