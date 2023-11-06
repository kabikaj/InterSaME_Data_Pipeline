#!/usr/bin/env python3
#
#    InterSaME_Data_Handler.py
#
# standalone gui for executing InterSaME pipeline
#
# gui for designing the app:
#   $ cd /usr/lib/x86_64-linux-gnu/qt5/bin/ 
#     ./designer
#
# usage:
#   $ pyinstaller --name="InterSaME_Data_Handler" --windowed InterSaME_Data_Handler.py
#     cp isame_indexes.json dist/InterSaME_Data_Handler
#     cp local_settings.py dist/InterSaME_Data_Handler
#     cp List-of-manuscript-fragments.md dist/InterSaME_Data_Handler
#     cp -r resources/ dist/InterSaME_Data_Handler
#     cd dist/InterSaME_Data_Handler ; ./InterSaME_Data_Handler
#
#######################################################################################

import re
import os
import sys
from contextlib import ExitStack
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAction, QMessageBox, QWidget, QTextEdit, QVBoxLayout, QPushButton

from isame_xml2txt import xml2txt
from isame_parser import parse
from isame_mapper import quran_map
from isame_json2tei import json2tei


class GUI(QMainWindow):

    def __init__(self):
        
        self.infile_paths = []

        self.xml_fpath = []
        self.txt_fpath = []
        self.pre_json_fpath = []
        self.json_fpath = []
        self.tei_fpath = []

        self.box_info = None
        self.debug_mode = False

        super().__init__()
        self.initUI()        

    def initUI(self):
        self.setWindowTitle('InterSaME Data Handler')
        self.setMinimumSize(QtCore.QSize(140, 40))
        #self.setGeometry(300, 300, 300, 220)
        self.statusBar().showMessage('Select New File to start conversion pipeline')
        self.resize(1200, 900)

        #
        # top menu
        #

        menu = self.menuBar()
        file_menu = menu.addMenu('&File')

        new_file = QAction('&New', self)        
        new_file.setStatusTip('New File')
        new_file.triggered.connect(self.open_dialog)

        about = QAction('&About', self)
        about.setStatusTip('About Information')
        about.triggered.connect(self.about_window)

        file_menu.addAction(new_file)
        file_menu.addAction(about)

        options_menu = menu.addMenu('&Options')

        debug_toggle = QAction('&Debug mode', self, checkable=True)
        debug_toggle.setChecked(False)
        debug_toggle.triggered.connect(self.toggleMenu)
        options_menu.addAction(debug_toggle)        

        #
        # processing box and run pipeline
        #

        self.info_box = QWidget(self)
        self.setCentralWidget(self.info_box)
        self.box_info = QTextEdit()
        self.box_info.setReadOnly(True)
        self.box_info.setPlainText('Select one or more files file using the menu File > New to run a new conversion pipeline on it.'
                                   '\nThe conversion pipeline is as follows:'
                                   '\n    Archetype .xml > InterSaME .txt > InterSaME .json > InterSaME TEI .xml'
                                   '\n Warning! If you select several files they will be processed in the order of selection')

        run_button = QPushButton('&RUN')
        #run_button.resize(self.run_button.sizeHint())
        #run_button.move(50, 50)
        layout = QVBoxLayout()
        layout.addWidget(self.box_info)
        layout.addWidget(run_button)
        self.info_box.setLayout(layout)
        run_button.clicked.connect(self.run_pipeline)

    def toggleMenu(self, state):
        if state:
            self.debug_mode = True
        else:
            self.debug_mode = False

    def open_dialog(self):
        fnames, _ = QFileDialog.getOpenFileNames(self, 'Open File', filter='Archetype xml (*.xml);;InterSaME txt file (*.txt);;InterSaME JSON file (*.json)')
        self.infile_paths = fnames

    def about_window(self):
        QMessageBox.about(self, "About InterSaME Data Handler", "This standalone application was created for the InterSaME Project.")

    def generate_output_fnames(self, fpath, fbase, fext, multiple):
        """ Generate the name of the output files, depending on the base name and the extension of the input file.

        (ID-1-ini.txt > ID-2-draft-pl.txt) > ID-3-trans.xml > ID-4.txt > ID-5-pre.json > ID-6.json > ID-7-tei.xml
                        ID-2-draft-ar.txt    ID-3-ref.xml

                                             ID.xml > ID.txt > ID-pre.json > ID.json > ID-tei.xml
    
        Args:
            fpath (str): path of input file.
            fbase (str): base name of input file.
            fext (str): extension of input file.
            multiple (bool): flag to indicate if there are more than one input files.
    
        """
        if multiple:
            base = fbase.partition('_')[0]
            if fext == '.xml':
                self.xml_fpath = self.infile_paths
                self.txt_fpath.append(f'{base}.txt')
                self.pre_json_fpath.append(f'{base}.pre.json')
                self.json_fpath.append(f'{base}.json')
                self.tei_fpath.append(f'{base}.xml')
            elif fext == '.txt':
                self.txt_fpath = self.infile_paths
                self.pre_json_fpath.append(f'{base}.pre.json')
                self.json_fpath.append(f'{base}.json')
                self.tei_fpath.append(f'{base}.xml')
            else:
                self.pre_json_fpath = self.infile_paths
                self.json_fpath.append(f'{base}.json')
                self.tei_fpath.append(f'{base}.xml')
        else:
            if (m := re.match(r'(.+?)-([1-9])(?:-.*)?', fbase)):
                base, n = m.groups()
                n = int(n)
        
                if fext == '.xml':
                    self.xml_fpath.append(fpath)
                    self.txt_fpath.append(os.path.join(fpath, f'{base}-{n+1}.txt'))
                    self.pre_json_fpath.append(os.path.join(fpath, f'{base}-{n+2}-pre.json'))
                    self.json_fpath.append(os.path.join(fpath, f'{base}-{n+3}.json'))
                    self.tei_fpath.append(os.path.join(fpath, f'{base}-{n+4}.xml'))
                elif fext == '.txt':
                    self.txt_fpath.append(fpath)
                    self.pre_json_fpath.append(os.path.join(fpath, f'{base}-{n+1}-pre.json'))
                    self.json_fpath.append(os.path.join(fpath, f'{base}-{n+2}.json'))
                    self.tei_fpath.append(os.path.join(fpath, f'{base}-{n+3}.xml'))
                else:
                    self.json_fpath.append(fpath)
                    self.tei_fpath.append(os.path.join(fpath, f'{base}-{n+1}.tei'))
            else:
                
                if fext == '.xml':
                    self.xml_fpath.append(fpath)
                    self.txt_fpath.append(os.path.join(fpath, f'{fbase}.txt'))
                    self.pre_json_fpath.append(os.path.join(fpath, f'{fbase}-pre.json'))
                    self.json_fpath.append(os.path.join(fpath, f'{fbase}.json'))
                    self.tei_fpath.append(os.path.join(fpath, f'{fbase}-tei.xml'))
                elif fext == '.txt':
                    self.txt_fpath.append(fpath)
                    self.pre_json_fpath.append(os.path.join(fpath, f'{fbase}-pre.json'))
                    self.json_fpath.append(os.path.join(fpath, f'{fbase}.json'))
                    self.tei_fpath.append(os.path.join(fpath, f'{fbase}-tei.xml'))
                else:
                    self.json_fpath.append(fpath)
                    self.tei_fpath.append(os.path.join(fpath, f'{fbase}-tei.xml'))

    def run_pipeline(self):
        if not self.infile_paths:
            self.box_info.append('Please, choose one or several files to run the pipeline on it')
            return

        fpath, fname = os.path.split(os.path.realpath(self.infile_paths[0]))
        base, ext = os.path.splitext(fname)
        MULTIPLE_FILES = len(self.infile_paths)!=1

        self.generate_output_fnames(fpath, base, ext, multiple=MULTIPLE_FILES)

        self.box_info.append(f'\n *************************************') 
        self.box_info.append(f' *  STARTING PIPELINE CONVERSION *')
        self.box_info.append(f' **************************************\n') 

        if ext == '.xml':

            self.box_info.append(f'Processing input file(s) {", ".join(self.xml_fpath)} ...')
            self.box_info.append(f'Converting xml file(s) to txt ...')

            if len(self.xml_fpath) == 1:
                with open(self.xml_fpath[0]) as xml_fp, open(self.txt_fpath[0], 'w') as txt_fp:
                    xml2txt(xml_fp, txt_fp)
                
            else:
                with ExitStack() as stack, open(self.txt_fpath[0], 'w') as txt_fp:
                    xml2txt([stack.enter_context(open(fn)) for fn in self.xml_fpath], txt_fp)

            self.box_info.append(f'Saving txt file as {self.txt_fpath} ...')
            self.box_info.append(f'\n >> XML TO TXT CONVERSION DONE\n')


        #FIXME update rest !!!!!!
        if ext in ('.xml', '.txt'):

            self.box_info.append(f'Converting txt file(s) to pre-json ...')
            self.box_info.append(f'Saving pre-json file(s) as {self.pre_json_fpath} ...')

            if len(self.txt_fpath) == 1:
                with open(self.txt_fpath[0]) as txt_fp, open(self.pre_json_fpath[0], 'w') as pre_json_fp: #FIXME TypeError: expected str, bytes or os.PathLike object, not list
                    try:
                        parse(txt_fp, pre_json_fp, debug=self.debug_mode)
                        if self.debug_mode:
                            with open('isame_parser.log') as parser_logfp:
                                self.box_info.append(parser_logfp.read())
                        self.box_info.append(f'\n >> TXT TO PRE-JSON CONVERSION DONE\n')
                    except Exception as e:
                        self.box_info.append(f'\nPARSING ABORTED!')
                        if not self.debug_mode:
                            self.box_info.append(f'Hint: Use debug mode to find the error.')
                        return
            else:
                with ExitStack() as stack, open(self.pre_json_fpath[0], 'w') as pre_json_fp:
                    try:
                        parse([stack.enter_context(open(fn)) for fn in self.txt_fpath], pre_json_fp, debug=self.debug_mode)
                        if self.debug_mode:
                            with open('isame_parser.log') as parser_logfp:
                                self.box_info.append(parser_logfp.read())
                    except Exception as e:
                        self.box_info.append(f'\nPARSING ABORTED!')
                        if not self.debug_mode:
                            self.box_info.append(f'Hint: Use debug mode to find the error.')
                        return

            self.box_info.append(f'Converting pre-json file(s) to json ...')
            self.box_info.append(f'Saving json file(s) as {self.json_fpath} ...')

            if len(self.txt_fpath) == 1:
                with open(self.pre_json_fpath[0]) as pre_json_fp, open(self.json_fpath[0], 'w') as json_fp:
                    try:
                        quran_map(pre_json_fp, json_fp, debug=self.debug_mode)
                        if self.debug_mode:
                            with open('isame_mapper.log') as mapper_logfp:
                                self.box_info.append(mapper_logfp.read())
                        self.box_info.append(f'\n >> PRE-JSON TO JSON CONVERSION DONE\n')
                    except Exception as e:
                        self.box_info.append(f'\nMAPPING ABORTED!')
                        if not self.debug_mode:
                            self.box_info.append(f'Hint: Use debug mode to find the error.')
                        return
            else:
                with ExitStack() as stack, open(self.json_fpath[0], 'w') as json_fp:
                    try:
                        parse([stack.enter_context(open(fn)) for fn in self.pre_json_fpath], json_fp, debug=self.debug_mode)
                        if self.debug_mode:
                            with open('isame_mapper.log') as mapper_logfp:
                                self.box_info.append(mapper_logfp.read())
                    except Exception as e:
                        self.box_info.append(f'\nMAPPING ABORTED!')
                        if not self.debug_mode:
                            self.box_info.append(f'Hint: Use debug mode to find the error.')
                        return

        if ext in ('.xml', '.txt', '.json'):

            self.box_info.append(f'Converting json file(s) to tei ...')
            self.box_info.append(f'Saving tei file(s) as {self.json_fpath} ...')

            if len(self.json_fpath) == 1:
                with open(self.json_fpath[0]) as json_fp, open(self.tei_fpath[0], 'w') as tei_fp:
                    try:
                        json2tei(json_fp, tei_fp)
                        if self.debug_mode:
                            with open('isame_json2tei.log') as json2tei_logfp:
                                self.box_info.append(json2tei_logfp.read())
                        self.box_info.append(f'\n >> JSON TO TEI CONVERSION DONE\n')
                    except Exception as e:
                        self.box_info.append(f'\nTEI CONVERSION ABORTED!')
                        #FIXME print ERRORS from log file!!
                        if not self.debug_mode:
                            self.box_info.append(f'Hint: Use debug mode to find the error.')
                        return
            else:
                with ExitStack() as stack, open(self.tei_fpath[0], 'w') as tei_fp:
                    try:
                        parse([stack.enter_context(open(fn)) for fn in self.json_fpath], tei_fp, debug=self.debug_mode)
                        if self.debug_mode:
                            with open('isame_json2tei.log') as json2tei_logfp:
                                self.box_info.append(json2tei_logfp.read())
                    except Exception as e:
                        self.box_info.append(f'\nMAPPING ABORTED!')
                        if not self.debug_mode:
                            self.box_info.append(f'Hint: Use debug mode to find the error.')
                        return

        self.box_info.append(f'\n ***************************') 
        self.box_info.append(f' * CONVERSION FINISHED *')
        self.box_info.append(f' ***************************\n') 


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())
