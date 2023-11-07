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
