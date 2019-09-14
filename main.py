#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#######################
## модули
from __future__ import unicode_literals
from __future__ import print_function
import sys
import os
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtUiTools import QUiLoader

import xml.etree.ElementTree as ET

import codecs # для поддержки utf-8 в содержимом файлов

#######################
## мои модули
from anapp import MGC_POS, MGC_Grammem, MGC_Ancode, MGC_FlexiaModel

###################################
## глобальные переменные
window = None # идея так себе, но сделаем основное окно глобальной переменной
session_file_name = 'session.log' # имя сессионого файла. В нём будут накапливаться новые леммы
qtcreator_main_form_file  = "design.ui" # основное окно

#######################
## классы

class MGC_XMLStuffHolder:
    '''
    Класс для всего, что касается xml
    '''
    ru_RU = 'ru_RU.xml' # имя файла со словарём
    ru_RU_old = 'ru_RU.xml.old' # имя файла со 'предыдущим' словарём

    tree = None
    root = None
    options = None
    prefixes = None
    lemmas = None

    @classmethod
    def loadPHPMorphyDictionary(cls):
        printLogLine('Loading phpMorphy XML dictionary...')
        cls.tree = ET.parse(cls.ru_RU)
        cls.root = cls.tree.getroot()
        printLogLine("... dictionary's loaded")
        #print root.tag, root.attrib
        #for child in root:
        #    print '---', child.tag, child.attrib

        cls.options = cls.root.find('options')
        cls.prefixes = cls.root.find('prefixes')
        cls.lemmas = cls.root.find('lemmas')

        # Части речи
        MGC_POS.buildPOSListFromXMLRoot(cls.root)

        # Граммемы
        MGC_Grammem.buildGrammemListFromXMLRoot(cls.root)

        # Анкоды
        MGC_Ancode.buildAncodeListFromXMLRoot(cls.root)

        # Флексии
        printLogLine('Loading flexia models...')
        MGC_FlexiaModel.buildFlexiaModelListFromXMLRoot(cls.root)
        printLogLine('... loaded')

class POSSearchTab(QtWidgets.QWidget):
    '''
    общий класс для влкладок с формами слова. Одна вкладка -- одна часть речи
    '''

    def __init__(self, name="POS", pos=None, meta_signature=[], lemma_edit=None, parent=None, super_ancodes_ids=[]):
        '''
        name -- название вкладки (часть речи)
        pos -- часть речи (экземпляр MGC_POS)
        meta_signature -- список списков граммем (экземпляров MGC_Grammem). будет использоваться при поиске подходящей модели флексий
        lemma_edit -- QLineEdit в которое вводится лемма
        super_ancodes_ids -- список супер (экстра, мета) анкодов. Из них можно выбрать тот, который будет относится ко ВСЕЙ лемме (то есть всем словам)
        '''
        QtWidgets.QWidget.__init__(self, parent)

        self.pos = pos
        self.meta_signature = meta_signature
        self.name = name
        self.super_ancodes_ids = super_ancodes_ids

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # для дочерних классов
        self.beforeSuffixList()

        self.suffix_list_layout = QtWidgets.QGridLayout()
        self.main_layout.addLayout(self.suffix_list_layout)

        self.suffix_list_layout.setColumnMinimumWidth(0, 40) # лемма
        self.suffix_list_layout.setColumnMinimumWidth(1, 5) # пустое место
        self.suffix_list_layout.setColumnMinimumWidth(2, 40) # окончание
        self.suffix_list_layout.setColumnMinimumWidth(3, 5) # пустое место
        self.suffix_list_layout.setColumnMinimumWidth(4, 40) # описание


        #добавить построчно элементы. Каждая строка имеет структуру label_1 edit label_2.
        # label_1 -- для отображения леммы, edit -- для ввода окончания, label_2 -- для отображения списка граммем
        self.lemma_labels = []
        self.suffix_edits = []
        self.descr_labels = []
        row = 0
        for ms in meta_signature:
            lbl = QtWidgets.QLabel()
            lbl.setText('*************')
            lemma_edit.textChanged.connect(lbl.setText)

            self.suffix_list_layout.addWidget(lbl, row, 0)
            self.lemma_labels.append(lbl)

            edt = QtWidgets.QLineEdit()
            self.suffix_list_layout.addWidget(edt, row, 2)
            self.suffix_edits.append(edt)

            lbl = QtWidgets.QLabel()
            txt = ''

            for grm in ms:
                txt = txt + ' ' + grm.name
            lbl.setText(txt)
            self.suffix_list_layout.addWidget(lbl, row, 4)
            self.descr_labels.append(lbl)
            row = row + 1

        # для дочерних классов
        self.afterSuffixList()

        # экстра анкоды для комбинации лемма + модель флексий
        # этот анкод никак не влияет на сигнатуру и не участвет в поиске моделей флексий
        self.super_ancodes_layout = QtWidgets.QGridLayout()
        self.main_layout.addLayout(self.super_ancodes_layout)

        self.super_ancodes_combo_box = QtWidgets.QComboBox()
        self.super_ancodes_list_widget = QtWidgets.QListWidget()

        self.super_ancodes_combo_box.currentIndexChanged.connect(self.superAncodeHasBeenChanged)

        self.super_ancodes_combo_box.addItem('Нет', userData=('', []))

        for said in self.super_ancodes_ids:
            # assert(said == MGC_Ancode.ancode_list[said].id)
            gl = []
            for g in MGC_Ancode.ancode_list[said].grammems:
                gl.append(g.long_name)
            self.super_ancodes_combo_box.addItem(MGC_Ancode.ancode_list[said].name + ': ' + str(MGC_Ancode.ancode_list[said].id), userData=(str(said), gl))

        self.super_ancodes_layout.addWidget(QtWidgets.QLabel('Мета анкод'), 0, 0)
        self.super_ancodes_layout.addWidget(self.super_ancodes_combo_box, 0, 1)
        self.super_ancodes_layout.addWidget(self.super_ancodes_list_widget, 1, 1)

    @QtCore.Slot()
    def superAncodeHasBeenChanged(self):
        self.super_ancodes_list_widget.clear()
        self.super_ancodes_list_widget.addItems(self.super_ancodes_combo_box.currentData()[1])

    def flush(self):
        for lbl in self.lemma_labels:
            lbl.setText('*************')

    def beforeSuffixList(self):
        '''
        этот метод дочерние классы могут перегрузить и добавить элементы до списка окончаний
        '''
        pass

    def afterSuffixList(self):
        '''
        этот метод дочерние классы могут перегрузить и добавить элементы после списка окончаний
        '''
        pass

    def extraGrammemsForSignature(self):
        '''
        этот метод дочерние классы могут перегрузить. Возвращает список списков граммем. Каждый список из этого списка добавится потом
        к построенной сигнатуре для поиска модели флексий. Первый список добавится к первому, второй ко второму и т.д.
        '''
        return None

    def getSignature(self):
        '''
        Построить сигнатуру. Сигнатура -- это список списков. Каждый список в сигнатуре описывает КАК и ЧТО получается из базы слова,
        элемент с индексом 0 (всегда!) каждого списка сигнатуры -- это пара (приставка, окончание), остальные
        элементы списка -- граммемы, описывающие слово, которое получается в результате подстановки этой приставки и этого окончания к
        базе слова. Cигнатура должна быть списком, а не словарём потому что в словаре не может быть двух записей с одинаковыми ключами,
        а в словообразовании такое возможно (например, для слова СЛОВ|О ('', 'А') -> [РОДИТЕЛЬНЫЙ ПАДЕЖ, ЕД. ЧИСЛО] -> СЛОВ|А и
        ('', 'А') -> [ИМИНИТЕЛЬНЫЙ ПАДЕЖ, МН. ЧИСЛО] -> СЛОВ|А)
        '''
        extra = self.extraGrammemsForSignature()

        signature = []
        # assertion:
        # len(self.suffix_edits) == len(self.meta_signature) (== len(extra) or extra == None)

        if extra != None:
            for i in range(len(self.meta_signature)):
                k = [('', self.suffix_edits[i].text().upper())]
                signature.append(k + self.meta_signature[i] + extra[i])
        else:
            for i in range(len(self.meta_signature)):
                k = [('', self.suffix_edits[i].text().upper())]
                signature.append(k + self.meta_signature[i])

        return signature

class NounSearchTab(POSSearchTab):
    def __init__(self, name="Сущесвительное", meta_signature=[], lemma_edit=None, parent=None, super_ancodes_ids=[]):
        '''
        name -- название вкладки (часть речи, например, "Сущесвительное")
        meta_signature -- список списков граммем (экземпляров MGC_Grammem). будет использоваться при поиске подходящей модели флексий
        lemma_edit -- QLineEdit в которое вводится лемма
        super_ancodes_ids -- список супер (экстра, мета) анкодов. Из них можно выбрать тот, который будет относится ко ВСЕЙ лемме (то есть всем словам)

        требуется, чтобы MGC_Grammem и MGC_POS уже были "прогружены"
        '''
        POSSearchTab.__init__(self, name, MGC_POS.getPOS('С'), meta_signature, lemma_edit, parent, super_ancodes_ids)

    def beforeSuffixList(self):
        self.gender_combo_box = QtWidgets.QComboBox()
        self.gender_combo_box.addItem('МР', userData=MGC_Grammem.getGrammem('МР'))
        self.gender_combo_box.addItem('ЖР', userData=MGC_Grammem.getGrammem('ЖР'))
        self.gender_combo_box.addItem('СР', userData=MGC_Grammem.getGrammem('СР'))
        self.gender_combo_box.addItem('Общий род', userData=MGC_Grammem.getGrammem('МР-ЖР'))
        self.main_layout.addWidget(self.gender_combo_box)

    def extraGrammemsForSignature(self):
        extra = [[self.gender_combo_box.currentData()] for i in range(len(self.meta_signature))]
        return extra

class AdjectiveSearchTab(POSSearchTab):
    def __init__(self, name="Прилагательное", meta_signature=[], lemma_edit=None, parent=None, super_ancodes_ids=[]):
        '''
        name -- название вкладки (часть речи, например, "Прилагательное")
        meta_signature -- список списков граммем (экземпляров MGC_Grammem). будет использоваться при поиске подходящей модели флексий
        lemma_edit -- QLineEdit в которое вводится лемма
        super_ancodes_ids -- список супер (экстра, мета) анкодов. Из них можно выбрать тот, который будет относится ко ВСЕЙ лемме (то есть всем словам)

        требуется, чтобы MGC_Grammem и MGC_POS уже были "прогружены"
        '''
        POSSearchTab.__init__(self, name, MGC_POS.getPOS('П'), meta_signature, lemma_edit, parent, super_ancodes_ids)

###################################
## глобальные функции
def printLogLine(s):
    #print(s)
    if (window != None) and (window.isVisible()):
        window.plainTextEdit.appendPlainText(s)
    else:
        print(s)

# функция для загрузки ресурсов. Мы планируем приложение упаковать в exe-шник вместе с design.ui, поэтому доставать его нужно специальным образом
# взято из https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile/44352931#44352931
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

@QtCore.Slot()
def searchFlexiaModels():
    '''
    функция для поиска моделей флексий по заданным в GUI параметрам
    '''
    signature = window.tabWidget.currentWidget().getSignature()

    flexia_model = MGC_FlexiaModel.buildFlexiaModelBySignature(window.tabWidget.currentWidget().pos, signature)

    flexia_models = MGC_FlexiaModel.findFlexiaModelsByFlexiaModel(flexia_model)

    window.comboBox_flexias.clear()

    for fm in flexia_models:
        window.comboBox_flexias.addItem('Модель № ' + str(fm.id), userData=fm)

@QtCore.Slot()
def printMorphedLemmaInTable():
    window.tableWidget_morphed.clearContents()
    lemma = window.lineEdit_lemma.text().upper()

    if window.comboBox_flexias.currentData() == None:
        #printLogLine('ОШИБКА: не выбрана модель флексий')
        # странное дело, слот срабатывает дважды и первый раз, когда currentData() == None !?!?!?
        # естественно, в такой ситуации ничего делать не нужно
        return

    list = window.comboBox_flexias.currentData().morph(body = lemma, to_list_of_tuples = True)

    window.tableWidget_morphed.setRowCount(len(list))

    index = 0
    for t in list:
        description = ''
        for g in t[1].grammems:
            description += (g.long_name + ' ')

        table_word = QtWidgets.QTableWidgetItem(t[0])
        table_descr = QtWidgets.QTableWidgetItem(description)
        window.tableWidget_morphed.setItem(index, 0, table_word)
        window.tableWidget_morphed.setItem(index, 1, table_descr)
        index += 1

@QtCore.Slot()
def addToTheList():
    lemma = window.lineEdit_lemma.text().upper()
    if lemma == None or lemma == '':
        printLogLine('ОШИБКА: пустая лемма')
        return
    fm = window.comboBox_flexias.currentData()
    ea = window.tabWidget.currentWidget().super_ancodes_combo_box.currentData() # там хранится пара (str(id), список_имён_граммем)
    if fm == None:
        printLogLine('ОШИБКА: не выбрана модель флексии')
    else:
        file = None
        try:
            file = codecs.open(session_file_name, mode='a', encoding='utf-8')
            record = lemma +':' + str(fm.id) + ':' + ea[0]
            file.write(record + '\n')
            printLogLine('Добавлена запись: "' + record + '"')
        except:
            printLogLine('ОШИБКА: возникли рудности при работе с файлом сессии. Внесение Записи в списко не гарантировано!')
        finally:
            if file != None and not (file.closed):
                file.close()

@QtCore.Slot()
def clearFlexiasAndTable():
    window.tableWidget_morphed.clearContents()
    window.comboBox_flexias.clear()

@QtCore.Slot()
def fromSessionFileToDict():
    '''
    По-хорошему эту функцию нужно вынести в отдельный поток
    '''
    session_file = None
    try:
        if (not os.path.isfile(session_file_name)) or (os.stat(session_file_name).st_size == 0):
            printLogLine('Сессионый файл пуст. Нечего переносить.')
            return

        printLogLine('Открываем сессионный файл')
        #session_file = open(session_file_name, 'r+') # r+, чтобы потом сделать truncate
        session_file = codecs.open(session_file_name, mode='r+', encoding='utf-8')

        printLogLine('Построчно переносим содержимое сессиного файла в дерево словаря')
        for l in session_file:
            parts = l.strip().split(':')
            MGC_XMLStuffHolder.lemmas[-1].tail = '\n\t\t'
            if (len(parts) < 3) or (parts[2].strip() == ''):
                se = ET.SubElement(MGC_XMLStuffHolder.lemmas, 'lemma', {'base': parts[0].strip(), 'flexia_id' : parts[1].strip()})
            else:
                se = ET.SubElement(MGC_XMLStuffHolder.lemmas, 'lemma', {'base': parts[0].strip(), 'flexia_id' : parts[1].strip(), 'ancode_id' : parts[2].strip()})
            se.tail = '\n\t'

        printLogLine('Очищаем содержимое сессионого файла и закрываем его')
        session_file.truncate(0)
        session_file.close()

        printLogLine('Переименовываем файл (ru_RU.xml --> ru_RU.xml.old)')
        os.replace(MGC_XMLStuffHolder.ru_RU, MGC_XMLStuffHolder.ru_RU_old)

        printLogLine('Записываем текущее дерево словаря в файл (ru_RU.xml)')
        MGC_XMLStuffHolder.tree.write(MGC_XMLStuffHolder.ru_RU, encoding = 'UTF-8')

    except:
        printLogLine('ОШИБКА: Произошла ошибка при работе с файлами!')
        printLogLine('ОШИБКА: Возможно, дальнейшая работа приложения будет затруднена!')
        printLogLine('ОШИБКА: Пожалуйста, скопируйте все сообщения здесь и покажите их разработчику')
        printLogLine('ОШИБКА: ' + str(sys.exc_info()[0]))
        printLogLine('ОШИБКА: ' + str(sys.exc_info()[1]))
        printLogLine('ОШИБКА: ' + str(sys.exc_info()[2]))
    finally:
        printLogLine('Закрываем все незакрытые файлы')
        if session_file != None and (not session_file.closed):
            session_file.close()

#######################
## основная программа
if __name__ == "__main__":
    # борьба за нормальное отображение русского в консоли
    if sys.version_info[0] == 2:
        reload(sys)
        sys.setdefaultencoding('utf8')

    qui_loader = QUiLoader() # загрузчик окна, берёт xml'ку и по ней строит окно
    main_form_file = QtCore.QFile(resource_path(qtcreator_main_form_file)) # ресурсы достаём специальным образом, так как они могут быть упакованы
    app = QtWidgets.QApplication(sys.argv)
    window = qui_loader.load(main_form_file, None)

    ################

    MGC_XMLStuffHolder.loadPHPMorphyDictionary()

    # список мета (супер, экстра) анкодов, которые можно приписывать паре лемма+модель флексии
    super_ancodes_ids = [662, 663, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 680, 681, 682, 683, 684, 685, 686, 687, 688, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 714, 715, 716, 717]

    # граммемы для сборки схем
    # ... падежи
    nominativ_grammem = MGC_Grammem.getGrammem('ИМ') # иминительный
    genitiv_grammem = MGC_Grammem.getGrammem('РД') # родительный
    accusative_grammem = MGC_Grammem.getGrammem('ВН') # винительный
    # ...рода
    masculinum_grammem = MGC_Grammem.getGrammem('МР')
    femininum_grammem = MGC_Grammem.getGrammem('ЖР')
    neutrum_grammem = MGC_Grammem.getGrammem('СР')
    # ...число
    pluralis_grammem = MGC_Grammem.getGrammem('МН')
    singularis_grammem = MGC_Grammem.getGrammem('ЕД')
    #...залог
    active_voice_grammem = MGC_Grammem.getGrammem('ДСТ')
    passiv_voice_grammem = MGC_Grammem.getGrammem('СТР')
    #...время
    present_grammem = MGC_Grammem.getGrammem('НСТ')
    past_grammem = MGC_Grammem.getGrammem('ПРШ')
    #...лицо
    first_person_grammem = MGC_Grammem.getGrammem('1Л')
    second_person_grammem = MGC_Grammem.getGrammem('2Л')
    #...наклонение
    imperative_grammem = MGC_Grammem.getGrammem('ПВЛ')


    # схемы (мета сигнатуры)
    # ...прилагательное
    adj_meta_signature = [
        [masculinum_grammem, nominativ_grammem, singularis_grammem],
        [femininum_grammem, nominativ_grammem, singularis_grammem],
        [neutrum_grammem, nominativ_grammem, singularis_grammem],
        [nominativ_grammem, pluralis_grammem],
    ]
    # ...существительное
    noun_meta_signature = [
        [nominativ_grammem, singularis_grammem],
        [genitiv_grammem, singularis_grammem],
        [accusative_grammem, singularis_grammem],
        [nominativ_grammem, pluralis_grammem],
    ]
    # ...существительное (множественное)
    noun_pl_meta_signature = [
        [nominativ_grammem, pluralis_grammem],
        [genitiv_grammem, pluralis_grammem],
        [accusative_grammem, pluralis_grammem],
    ]
    # ...глагол
    verb_meta_sifnature = [
        [active_voice_grammem, present_grammem, first_person_grammem, singularis_grammem,],
        [active_voice_grammem, past_grammem, masculinum_grammem, singularis_grammem],
        [active_voice_grammem, imperative_grammem, second_person_grammem, pluralis_grammem],
    ]
    # ...причастие
    part_meta_signature = [
        [active_voice_grammem, present_grammem, singularis_grammem, masculinum_grammem, nominativ_grammem],
        [passiv_voice_grammem, present_grammem, singularis_grammem, masculinum_grammem, nominativ_grammem],
    ]

    noun_tab = NounSearchTab(name = 'Сущ.', meta_signature=noun_meta_signature, lemma_edit=window.lineEdit_lemma, super_ancodes_ids=super_ancodes_ids)
    adj_tab = AdjectiveSearchTab(name = 'Прил.', meta_signature=adj_meta_signature, lemma_edit=window.lineEdit_lemma, super_ancodes_ids=super_ancodes_ids)
    noun_pl_tab = POSSearchTab(name="Сущ. (множ.)", pos=MGC_POS.getPOS('С'), meta_signature=noun_pl_meta_signature, lemma_edit=window.lineEdit_lemma, parent=None, super_ancodes_ids=super_ancodes_ids)
    verb_tab = POSSearchTab(name="Глагол", pos=MGC_POS.getPOS('Г'), meta_signature=verb_meta_sifnature, lemma_edit=window.lineEdit_lemma, parent=None, super_ancodes_ids=super_ancodes_ids)
    part_tab = POSSearchTab(name="Прич.", pos=MGC_POS.getPOS('ПРИЧАСТИЕ'), meta_signature=part_meta_signature, lemma_edit=window.lineEdit_lemma, parent=None, super_ancodes_ids=super_ancodes_ids)

    window.tabWidget.addTab(noun_tab, noun_tab.name)
    window.tabWidget.addTab(noun_pl_tab, noun_pl_tab.name)
    window.tabWidget.addTab(adj_tab, adj_tab.name)
    window.tabWidget.addTab(verb_tab, verb_tab.name)
    window.tabWidget.addTab(part_tab, part_tab.name)

    window.tableWidget_morphed.setColumnCount(2)
    window.tableWidget_morphed.setRowCount(0)
    window.tableWidget_morphed.setHorizontalHeaderLabels(['Слово', 'Граммемы'])

    window.pushButton_search.clicked.connect(searchFlexiaModels)
    window.comboBox_flexias.currentIndexChanged.connect(printMorphedLemmaInTable)
    window.pushButton_add.clicked.connect(addToTheList)
    window.tabWidget.currentChanged.connect(clearFlexiasAndTable)
    window.pushButton_to_dict.clicked.connect(fromSessionFileToDict)

    ################

    window.show()
    sys.exit(app.exec_())
