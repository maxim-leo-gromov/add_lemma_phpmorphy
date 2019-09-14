#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
from __future__ import unicode_literals
from __future__ import print_function
import xml.etree.ElementTree as ET

import sys


##########################################################
class MGC_POS:
    """ класс для хранения 'части речи' """
    
    # список частей речи, список упорядочен по id, индекс pos в списке равен его id
    pos_list = None

    # сопоставление коротких phpMorphy'евских имён длинным инменам
    short_to_long_name_mapping = {
        'С'             :'существительное',
        'П'             :'прилагательное',
        'КР_ПРИЛ'       :'краткое прилагательное',
        'ИНФИНИТИВ'     :'инфинитив',
        'Г'             :'глагол в личной форме',
        'ДЕЕПРИЧАСТИЕ'  :'деепричастие',
        'ПРИЧАСТИЕ'     :'причастие',
        'КР_ПРИЧАСТИЕ'  :'краткое причастие',
        'МС'            :'местоимение-существительное',
        'МС-П'          :'местоименное прилагательное',
        'МС-ПРЕДК'      :'местоимение-предикатив',
        'ЧИСЛ'          :'числительное (количественное)',
        'ЧИСЛ-П'        :'порядковое числительное ',
        'Н'             :'наречие ',
        'ПРЕДК'         :'предикатив',
        'ПРЕДЛ'         :'предлог',
        'ПОСЛ'          :'????',
        'СОЮЗ'          :'союз',
        'МЕЖД'          :'междометие',
        'ЧАСТ'          :'частица',
        'ВВОДН'         :'вводное слово',
        'ФРАЗ'          :'фразеологизм',
        ''              :'{мета}'
    }

    def __init__(self, an_xml_pos = None):
        if an_xml_pos == None:
            self.id = None
            self.name = None
            self.is_predict = None
            self.long_name = None
        else:
            self.id          = int(an_xml_pos.attrib['id'])
            self.name        = an_xml_pos.attrib['name']
            self.is_predict  = int(an_xml_pos.attrib['is_predict'])
            #self.long_name   = self.short_to_long_name_mapping[pos.attrib['name']]
            self.long_name   = self.short_to_long_name_mapping[self.name]            
    
    def fancyPrint(self):
        print('------------ pos -------------')
        print('ID: {0}'.format(self.id))
        print('Name: ' + self.name)
        print('Long Name: ' + self.long_name)
        print('is_predict: {0}'.format(self.is_predict))
        print('------------------------------')
    
    @classmethod    
    def buildPOSListFromXMLRoot(cls, xml_root = None):
        ''' построить список pos по XML. Список хранится внутри '''
        # Части речи. Узнаём кол-во записей по-тупому. Хотим добиться
        # чтобы индекс элемента совпадал с его id
        if xml_root == None:
            return
        
        max_id = 0
        for pos in xml_root.find('poses').findall('pos'):
            if max_id < int(pos.attrib['id']):
                max_id = int(pos.attrib['id'])
                
        cls.pos_list = [None] * (max_id + 1) # идентификаторы начинаются с 0
        
        for pos in xml_root.find('poses').findall('pos'):
            a = MGC_POS(pos)
            cls.pos_list[a.id] = a
    
    @classmethod
    def getPOS(cls, pos_name = 'П'):
        ''' id pos по короткому имени'''
        for pos in cls.pos_list:
            if (pos != None) and (pos.name == pos_name):
                return pos
        return None

##########################################################
class MGC_Grammem:
    """ класс для хранения граммемы """
    
    # список граммем, список упорядочен по id, индекс граммемы в списке равен его id
    grammem_list = None
    
    # сопоставление коротких phpMorphy'евских имён длинным инменам
    short_to_long_name_mapping = {
        'МР'    :'мужской род',
        'ЕД'    :'единственное число',
        'ИМ'    :'именительный',
        'РД'    :'родительный',
        '2'     :'второй родительный или второй предложный падежи',
        'ДТ'    :'дательный',
        'ВН'    :'винительный',
        'ТВ'    :'творительный',
        'ПР'    :'предложный',
        'ЗВ'    :'звательный',
        'МН'    :'множественное число',
        '0'     :'неизменяемое',
        'РАЗГ'  :'разговорный',
        'АРХ'   :'архаизм',
        'МР-ЖР' :'общий род',
        'ЖР'    :'женский род',
        'СР'    :'средний род',
        'АББР'  :'аббревиатура',
        'ИМЯ'   :'имя',
        'ОТЧ'   :'отчество',
        'ОД'    :'одушевленное',
        'НО'    :'неодушевленное',
        'СРАВН' :'сравнительная степень (для прилагательных)',
        'ПРЕВ'  :'превосходная степень (для прилагательных)',
        'БЕЗЛ'  :'безличный глагол',
        'БУД'   :'будущее время',
        'ПРШ'   :'прошедшее время',
        'НСТ'   :'настоящее время',
        'ДСТ'   :'действительный залог',
        '1Л'    :'первое лицо',
        '2Л'    :'второе лицо',
        '3Л'    :'третье лицо',
        'ПВЛ'   :'повелительное наклонение (императив)',
        'СТР'   :'страдательный залог',
        'ВОПР'  :'вопросительное наречие',
        'УКАЗАТ':'указательное наречие',
        'ЛОК'   :'топоним',
        'КАЧ'   :'качественное прилагательное',
        'ДФСТ'  :'??? прилагательное (не используется)',
        'ОРГ'   :'организация',
        'СВ'    :'совершенный вид',
        'ПЕ'    :'переходный (возможно в phpMorphy значение перепутано с непереходным)',
        'НП'    :'непереходный (возможно в phpMorphy значение перепутано с переходным)',
        'НС'    :'несовершенный вид',
        'ЖАРГ'  :'жаргонизм',
        'ОПЧ'   :'опечатка',
        'ФАМ'   :'фамилия',
        'ПРИТЯЖ':'притяжательное (не используется)',
        'ПОЭТ'  :'поэтическое',
        'ПРОФ'  :'профессионализм',
        'ПОЛОЖ' : 'положительная степень (?)'
    }

    def __init__(self, an_xml_grammem = None):
        if an_xml_grammem == None:
            self.id = None
            self.name = None
            self.shift = None
            self.long_name = None
        else:
            self.id          = int(an_xml_grammem.attrib['id'])
            self.name        = an_xml_grammem.attrib['name']
            self.shift  = int(an_xml_grammem.attrib['shift'])
            self.long_name   = self.short_to_long_name_mapping[self.name]            
    
    def fancyPrint(self):
        print('------------ grammem -------------')
        print('ID: {0}'.format(self.id))
        print('Name: ' + self.name)
        print('Long Name: ' + self.long_name)
        print('shift: {0}'.format(self.shift))
        print('----------------------------------')
        
    @classmethod
    def buildGrammemListFromXMLRoot(cls, xml_root = None):
        if xml_root == None:
            return
        
        max_id = 0
        for grammem in xml_root.find('grammems').findall('grammem'):
            if max_id < int(grammem.attrib['id']):
                max_id = int(grammem.attrib['id'])
                
        cls.grammem_list = [None] * (max_id + 1)
        
        for grammem in xml_root.find('grammems').findall('grammem'):
            a = MGC_Grammem(grammem)
            cls.grammem_list[a.id] = a
            
    @classmethod
    def getGrammem(cls, grammem_name = 'МР'):
        ''' grammem по короткому имени'''
        for grammem in cls.grammem_list:
            if (grammem != None) and (grammem.name == grammem_name):
                return grammem
        return None

##########################################################
class MGC_Ancode:
    """ класс для хранения анкодов """
    
    ancode_list = None
    
    def __init__(self, an_xml_ancode = None, pos_list = None, grammem_list = None):
        if (an_xml_ancode == None) or (pos_list == None) or (grammem_list == None):
            self.id = None
            self.name = None
            self.pos = None
            self.grammems = None
        else:
            self.id         = int(an_xml_ancode.attrib['id'])
            self.name       = an_xml_ancode.attrib['name']
            self.pos        = pos_list[int(an_xml_ancode.attrib['pos_id'])]
            self.grammems = []
            for grammem in an_xml_ancode.findall('grammem'):
                self.grammems.append(grammem_list[int(grammem.attrib['id'])])             
    
    def fancyPrint(self):
        print('------------ ancode -------------')
        print('ID: {0}'.format(self.id))
        print('Name: ' + self.name)
        print('POS: ' + self.pos.long_name)
        for grammem in self.grammems:
            print('  |-->' + grammem.long_name)
        print('---------------------------------')
        
    def inlinePrint(self):
        print(self.pos.long_name, end = ' :: ')
        for grammem in self.grammems:
            print(grammem.long_name, end = ', ')
        print()
        
    @classmethod
    def buildAncodeListFromXMLRoot(cls, xml_root = None):
        if xml_root == None:
            return
        
        if MGC_POS.pos_list == None:
            print('POSes are not preloaded. Loading.')
            MGC_POS.buildPOSListFromXMLRoot(xml_root)
        
        if MGC_Grammem.grammem_list == None:
            print('Grammems are not preloaded. Loading.')
            MGC_Grammem.buildGrammemListFromXMLRoot(xml_root)
        
        max_id = 0
        for ancode in xml_root.find('ancodes').findall('ancode'):
            if max_id < int(ancode.attrib['id']):
                max_id = int(ancode.attrib['id'])
                
        cls.ancode_list = [None] * (max_id + 1)
        
        for ancode in xml_root.find('ancodes').findall('ancode'):
            #print("'" + grammem.attrib['name'] + "'    :'',")
            a = MGC_Ancode(ancode, MGC_POS.pos_list, MGC_Grammem.grammem_list)
            cls.ancode_list[a.id] = a
        #ancode_list[0].fancyPrint()


##########################################################
class MGC_FlexiaModel:
    """ класс для хранения моделей флексий """
    
    class MGC_Flexia:
        """ класс для хранения флексий """
        def __init__(self, an_xml_flexia = None, ancode_list = None):
            if (an_xml_flexia == None) or (ancode_list == None):
                self.prefix = None
                self.suffix = None
                self.ancode = None
            else:
                self.prefix     = an_xml_flexia.attrib['prefix']
                self.suffix     = an_xml_flexia.attrib['suffix']
                self.ancode     = ancode_list[int(an_xml_flexia.attrib['ancode_id'])]
        
        def fancyPrint(self):
            print('------------ flexia -------------')
            print('prefix: ' + self.prefix)
            print('suffix: ' + self.suffix)
            self.ancode.inlinePrint()
            print('---------------------------------')
            
        def inlinePrint(self):
            print(self.prefix + '****' + self.suffix + ' --> ', end = '')
            self.ancode.inlinePrint()
            
        def morph(self, body = 'абыр', to_str_tuple = False):
            if to_str_tuple:
                tuple = (self.prefix + body + self.suffix, self.ancode)
                return tuple
            else:
                print(self.prefix + body + self.suffix + ' --> ', end = '')
                self.ancode.inlinePrint()
                return None
            
        def isOtherFlexiaSubSetOfThis(self, other):
            ''' проверяет, является ли другая флексия подмножеством этой в смысле анкодов
            проверяется, что совпадают приставка и окончание. Анкоды у обоих должны быть взяты из 
            MGC_Ancode.ancode_list (соответственно, граммемы в анкодах взяты из MGC_Grammem.grammem_list,
            а pos из MGC_POS.pos_list). Ни pos, ни gramme не должны быть None '''
            
            if (self.prefix != other.prefix) or (self.suffix != other.suffix):
                return False
            if self.ancode.pos.id != other.ancode.pos.id:
                return False
            for g in other.ancode.grammems:
                if g not in self.ancode.grammems:
                    return False
            return True
    
    flexia_model_list = None
    
    def __init__(self, an_xml_flexia_model = None, ancode_list = None):
        if (an_xml_flexia_model == None) or (ancode_list == None):
            self.id = None
            self.flexias = None
        else:
            self.id         = int(an_xml_flexia_model.attrib['id'])
            self.flexias    = []
            for flexia in an_xml_flexia_model.findall('flexia'):
                self.flexias.append(MGC_FlexiaModel.MGC_Flexia(flexia, ancode_list))             
    
    def fancyPrint(self):
        print('------------ flexia_model -------------')
        if self.id != None:
            print('ID: {0}'.format(self.id))
        else:
            print ('ID: None')
        for flexia in self.flexias:
            flexia.inlinePrint()
        print('---------------------------------------')
    
    def morph(self, body = 'абыр', to_list_of_tuples = False):
        if to_list_of_tuples:
            list = []
            for flexia in self.flexias:
                list.append(flexia.morph(body, to_str_tuple = True))
            return list
        else:
            for flexia in self.flexias:
                flexia.morph(body)
            return None

    @classmethod
    def buildFlexiaModelListFromXMLRoot(cls, xml_root = None):
        ''' построить список flexia_model по XML. Список хранится внутри '''
        if xml_root == None:
            return
        
        if MGC_Ancode.ancode_list == None:
            print('Ancodes are not preloaded. Loading')
            MGC_Ancode.buildAncodeListFromXMLRoot(root)
        
        cls.flexia_model_list = []
        for flexia_model in xml_root.find('flexias').findall('flexia_model'):
            #print("'" + grammem.attrib['name'] + "'    :'',")
            a = MGC_FlexiaModel(flexia_model, MGC_Ancode.ancode_list)
            cls.flexia_model_list.append(a)
     
    @classmethod       
    def buildFlexiaModelBySignature(cls, pos = None, grammem_signature = None):
        '''
        Построить модель флексий по сигнатуре.
        Сигнатура -- это список списков. Каждый список в сигнатуре описывает КАК и ЧТО получается из базы слова,
        элемент с индексом 0 (всегда!) каждого списка сигнатуры -- это пара (приставка, окончание), остальные
        элементы списка -- граммемы, описывающие слово, которое получается в результате подстановки этой приставки и этого окончания к
        базе слова. Cигнатура должна быть списком, а не словарём потому что в словаре не может быть двух записей с одинаковыми ключами,
        а в словообразовании такое возможно (например, для слова СЛОВ|О ('', 'А') -> [РОДИТЕЛЬНЫЙ ПАДЕЖ, ЕД. ЧИСЛО] -> СЛОВ|А и
        ('', 'А') -> [ИМИНИТЕЛЬНЫЙ ПАДЕЖ, МН. ЧИСЛО] -> СЛОВ|А)
        '''
        if (pos == None) or (grammem_signature == None):
            return None
        model = MGC_FlexiaModel()
        model.flexias = []
        
        for grms in grammem_signature:
            #print(grms)
            f = MGC_FlexiaModel.MGC_Flexia()
            f.prefix = grms[0][0]
            f.suffix = grms[0][1]
            f.ancode = MGC_Ancode()
            f.ancode.pos = pos
            f.ancode.grammems = grms[1:]
            model.flexias.append(f)
        return model
    
    def isOtherModelSubsetOfThis(self, other = None):
        if other == None:
            return True
        for o_f in other.flexias:
            flag = False
            for t_f in self.flexias:
                if t_f.isOtherFlexiaSubSetOfThis(o_f):
                    flag = True
                    break
            if not flag:
                return False
        return True

    
    @classmethod
    def findFlexiaModelsByFlexiaModel(cls, given_model = None):
        if given_model == None:
            return cls.flexia_model_list
        result = [f for f in cls.flexia_model_list if f.isOtherModelSubsetOfThis(given_model)]
        return result
        


    
