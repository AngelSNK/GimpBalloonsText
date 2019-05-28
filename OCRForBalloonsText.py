#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gimpfu import *
from string import Template
import codecs
import subprocess
import re
import glob
import inspect
import sys
import os
import traceback
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import SimpleHTTPServer
import SocketServer
import HTMLParser
import cgi
import xml.etree.ElementTree as ET
import urllib
import threading
import tempfile
import datetime
import time
from io import BytesIO
from os import sep
Path = tempfile.gettempdir()
#Path Plugin GIMP
PathPlugin = os.path.dirname(inspect.getfile(inspect.currentframe()))
nameFile = u"OcrImage"
EXTENSIONOCR = u".png"
TXT=u".txt"
HOCR=u".hocr"
T_TXT=u"-T.txt"
BText = "BText"#Tag ballon WHITE/EMPTY
g_nameDocument = u"MyDocument"
nameFileImageOCR = nameFile + EXTENSIONOCR
nameFileTXTOCR = nameFile
nameFileTranslation = nameFile + T_TXT
OK = "ok.txt"
FILEASS = "subtitle.ass"
FILEAVS = "video.avs"
bPathTranslation = "BTranslation"
g_pathProyectWeb=""
g_typeFont=""
g_sizeFont=""
g_colorFont=""
g_SelectionOCR=""
PORT = 8000
IP="127.0.0.1"
CARRIAGERETURN="\r\n"
TAGPATHSTROKE=u"_PS_"
TAGPREFIXGROUP = u"G_"
g_activeLayer = None
g_imageActive = None
LayerGroup = None
pathProyect = ""
namePageHTML = "EditOCRText.html"
pathFilesImageOcr=[]
programOCR=[]
pathTessdata=[]
argsOCR=[]
nameEngineOCR=["EMPTY"]
programWeb=[""]
optionsWeb=[""]
sConfigurationIni=""
selectionEngineOCRINI=0
selectionCase = ("none","lowercase", "UPPERCASE", "Capitalize", "Sentence")
SELECTIONEDIT = ("none","Edit HTA/IE","Edit WebNavigator","Edit Subtitle(ASS)")
SelectionOCR = ("OCR Selection", "OCR All layers/Path","Only Edit Text","Update Language")
pathFileINI = PathPlugin + r"\OCRForBalloonsText.ini"
def WriteFileUTF(pathFile,Text):
    try:
        if not os.path.exists(os.path.dirname(pathFile)):
            os.makedirs(os.path.dirname(pathFile))
        f = codecs.open(pathFile,"w", encoding='utf-8')
        f.write(Text)
        f.close()
    except Exception as e:
        pdb.gimp_message("Error WRITE:"  + str(traceback.format_exc()) + CARRIAGERETURN + pathFile + CARRIAGERETURN + Text )    
        pass
def ReadFileUTF(pathFile):
    try:
        f = codecs.open(pathFile, encoding='utf-8-sig')
        Text = f.read()
        f.close()
        return Text
    except Exception as e:
        pdb.gimp_message("ERROR READ:" +  str(traceback.format_exc())  )    
        return ""
DEFAULTINI = """[OCR TESSERACT]
ProgramOCR = "OCR\tesseract.exe"
PathTessdata= "OCR\tessdata"
ArgsOCR="${NAMEFILEIMAGEOCR} ${NAMEFILEOUTOCR} --psm ${ORIENTATION} --tessdata-dir ${PATHTESSDATA} -l ${DESTLANGUAGEOCR} hocr"
[OCR TESSERACT 4.1]
ProgramOCR = "C:\Program Files\Tesseract-OCR\tesseract.exe"
PathTessdata= ""
ArgsOCR="${NAMEFILEIMAGEOCR} ${NAMEFILEOUTOCR} --psm ${ORIENTATION} -l ${DESTLANGUAGEOCR} hocr"
[OCR CAPTURE2TEXT]
ProgramOCR = "OCR\Capture2Text_CLI.exe"
PathTessdata= ""
ArgsOCR="-l ${DESTLANGUAGEFULLOCR} -i ${NAMEFILEIMAGEOCR} -o ${NAMEFILEOUTOCR}.txt ${ORIENTATIONVERTICAL} "

[Navigator Chrome]
ProgramWeb = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
OptionsWeb = "--new-window --user-data-dir="%appdata%\OCRChrome""

[CONFIGURATION]
selectionEngineOCR = 0
"""        
def loadFileINI():
    global nameEngineOCR,programOCR,pathTessdata,argsOCR,programWeb,optionsWeb,selectionEngineOCRINI
    nameEngineOCR=["empty"]
    programOCR=[""]
    pathTessdata=[""]
    argsOCR=[""]
    programWeb=[""]
    optionsWeb=[""]
    if os.path.exists(pathFileINI):
        textINI = ReadFileUTF(pathFileINI)
        nameEngineOCR = re.findall(r'\[OCR(.*)?]',textINI,re.IGNORECASE)
        programOCR = re.findall(r'ProgramOCR.*?"(.*?)"',textINI,re.IGNORECASE)
        pathTessdata = re.findall(r'PathTessdata.*?"(.*?)"',textINI,re.IGNORECASE)
        argsOCR = re.findall(r'ArgsOCR.*?"(.*?)"',textINI,re.IGNORECASE)
        programWeb=re.findall(r'ProgramWeb.*?"(.*)"',textINI,flags=re.IGNORECASE)
        optionsWeb=re.findall(r'OptionsWeb.*?"(.*)"',textINI,flags=re.IGNORECASE)
        aSel=re.findall(r'selectionEngineOCR.*?(\d+)',textINI,flags=re.IGNORECASE)
        selectionEngineOCRINI = int(aSel[0]) if aSel else 0
    else:
        WriteFileUTF(pathFileINI,DEFAULTINI)
def saveFileINI(indexEngineOCR):
    textINI = ReadFileUTF(pathFileINI)
    if textINI.lower().find(  "selectionEngineOCR".lower() )>=0:
        textINI = re.sub("(selectionEngineOCR.*=.*?)(\d+)","\g<1>{}".format(indexEngineOCR),textINI, flags=re.IGNORECASE)
    else:
        textINI = textINI.replace("[CONFIGURATION]","") + CARRIAGERETURN +"[CONFIGURATION]" + CARRIAGERETURN + "selectionEngineOCR = {}".format(indexEngineOCR)
    WriteFileUTF(pathFileINI,textINI)
loadFileINI()

languagueCode = {
    # 'af': 'afrikaans',
    # 'sq': 'albanian',
    # 'am': 'amharic',
    # 'ar': 'arabic',
    # 'hy': 'armenian',
    # 'az': 'azerbaijani',
    # 'eu': 'basque',
    # 'be': 'belarusian',
    # 'bn': 'bengali',
    # 'bs': 'bosnian',
    # 'bg': 'bulgarian',
    # 'ca': 'catalan',
    # 'ceb': 'cebuano',
    # 'ny': 'chichewa',
    # 'zh-cn': 'chinese (simplified)',
    # 'zh-tw': 'chinese (traditional)',
    # 'co': 'corsican',
    # 'hr': 'croatian',
    # 'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    # 'eo': 'esperanto',
    # 'et': 'estonian',
    # 'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'french',
    # 'fy': 'frisian',
    # 'gl': 'galician',
    # 'ka': 'georgian',
    'de': 'german',
    # 'el': 'greek',
    # 'gu': 'gujarati',
    # 'ht': 'haitian creole',
    # 'ha': 'hausa',
    # 'haw': 'hawaiian',
    # 'iw': 'hebrew',
    # 'hi': 'hindi',
    # 'hmn': 'hmong',
    # 'hu': 'hungarian',
    # 'is': 'icelandic',
    # 'ig': 'igbo',
    # 'id': 'indonesian',
    # 'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    # 'jw': 'javanese',
    # 'kn': 'kannada',
    # 'kk': 'kazakh',
    # 'km': 'khmer',
    'ko': 'korean',
    # 'ku': 'kurdish (kurmanji)',
    # 'ky': 'kyrgyz',
    # 'lo': 'lao',
    # 'la': 'latin',
    # 'lv': 'latvian',
    # 'lt': 'lithuanian',
    # 'lb': 'luxembourgish',
    # 'mk': 'macedonian',
    # 'mg': 'malagasy',
    # 'ms': 'malay',
    # 'ml': 'malayalam',
    # 'mt': 'maltese',
    # 'mi': 'maori',
    # 'mr': 'marathi',
    # 'mn': 'mongolian',
    # 'my': 'myanmar (burmese)',
    # 'ne': 'nepali',
    # 'no': 'norwegian',
    # 'ps': 'pashto',
    # 'fa': 'persian',
    # 'pl': 'polish',
    'pt': 'portuguese',
    # 'pa': 'punjabi',
    # 'ro': 'romanian',
    'ru': 'russian',
    # 'sm': 'samoan',
    # 'gd': 'scots gaelic',
    # 'sr': 'serbian',
    # 'st': 'sesotho',
    # 'sn': 'shona',
    # 'sd': 'sindhi',
    # 'si': 'sinhala',
    # 'sk': 'slovak',
    # 'sl': 'slovenian',
    # 'so': 'somali',
    'es': 'spanish',
    # 'su': 'sundanese',
    # 'sw': 'swahili',
    # 'sv': 'swedish',
    # 'tg': 'tajik',
    # 'ta': 'tamil',
    # 'te': 'telugu',
    # 'th': 'thai',
    # 'tr': 'turkish',
    # 'uk': 'ukrainian',
    # 'ur': 'urdu',
    # 'uz': 'uzbek',
    # 'vi': 'vietnamese',
    # 'cy': 'welsh',
    # 'xh': 'xhosa',
    # 'yi': 'yiddish',
    # 'yo': 'yoruba',
    # 'zu': 'zulu',
    # 'fil': 'Filipino',
    # 'he': 'Hebrew'
}

LanguagesOCR = {
    "afr": "Afrikaans",
    "sqi": "Albanian",
    "amh": "Amharic",
    "grc": "Ancient Greek",
    "ara": "Arabic",
    "asm": "Assamese",
    "aze_cyrl": "Azerbaijani (Alternate)",
    "aze": "Azerbaijani",
    "eus": "Basque",
    "bel": "Belarusian",
    "ben": "Bengali",
    "bos": "Bosnian",
    "bul": "Bulgarian",
    "mya": "Burmese",
    "cat": "Catalan",
    "ceb": "Cebuano",
    "khm": "Central Khmer",
    "chr": "Cherokee",
    "chi_sim": "Chinese - Simplified",
    "chi_tra": "Chinese - Traditional",
    "hrv": "Croatian",
    "ces": "Czech",
    "dan_frak": "Danish (Alternate)",
    "dan": "Danish",
    "nld": "Dutch",
    "dzo": "Dzongkha",
    "eng": "English",
    "epo": "Esperanto",
    "est": "Estonian",
    "fin": "Finnish",
    "frk": "Frankish",
    "fra": "French",
    "glg": "Galician",
    "kat_old": "Georgian (Old)",
    "kat": "Georgian",
    "deu_frak": "German (Alternate)",
    "deu": "German",
    "ell": "Greek",
    "guj": "Gujarati",
    "hat": "Haitian",
    "heb": "Hebrew",
    "hin": "Hindi",
    "hun": "Hungarian",
    "isl": "Icelandic",
    "inc": "Indic",
    "ind": "Indonesian",
    "iku": "Inuktitut",
    "gle": "Irish",
    "ita_old": "Italian (Old)",
    "ita": "Italian",
    "jpn": "Japanese",
    "jpn_vert": "Japanese Vert",
    "jav": "Javanese",
    "kan": "Kannada",
    "kaz": "Kazakh",
    "kir": "Kirghiz",
    "kor": "Korean",
    "kru": "Kurukh",
    "lao": "Lao",
    "lat": "Latin",
    "lav": "Latvian",
    "lit": "Lithuanian",
    "mkd": "Macedonian",
    "msa": "Malay",
    "mal": "Malayalam",
    "mlt": "Maltese",
    "mar": "Marathi",
    "equ": "Math/Equations",
    "enm": "Middle English (1100-1500)",
    "frm": "Middle French (1400-1600)",
    "nep": "Nepali",
    "nor": "Norwegian",
    "ori": "Odiya",
    "pan": "Panjabi",
    "fas": "Persian",
    "pol": "Polish",
    "por": "Portuguese",
    "pus": "Pushto",
    "ron": "Romanian",
    "rus": "Russian",
    "san": "Sanskrit",
    "srp": "Serbian",
    "sin": "Sinhala",
    "slk_frak": "Slovak (Alternate)",
    "slk": "Slovak",
    "slv": "Slovenian",
    "spa_old": "Spanish (Old)",
    "spa": "Spanish",
    "srp_latn": "srp_latn",
    "swa": "Swahili",
    "swe": "Swedish",
    "syr": "Syriac",
    "tgl": "Tagalog",
    "tgk": "Tajik",
    "tam": "Tamil",
    "tel": "Telugu",
    "tha": "Thai",
    "bod": "Tibetan",
    "tir": "Tigrinya",
    "tur": "Turkish",
    "uig": "Uighur",
    "ukr": "Ukrainian",
    "urd": "Urdu",
    "uzb_cyrl": "Uzbek (Alternate)",
    "uzb": "Uzbek",
    "vie": "Vietnamese",
    "cym": "Welsh",
    "yid": "Yiddish"
}
LanguageOCRAvaible = ()
os.chdir(PathPlugin)
if programOCR:
    selectionEngineOCRINI = selectionEngineOCRINI if selectionEngineOCRINI<len(programOCR) else 0
    if (os.path.isfile(programOCR[selectionEngineOCRINI])):
        Command = [ programOCR[selectionEngineOCRINI] ]
        bCapture2Text=False
        if programOCR[selectionEngineOCRINI].find("tesseract")>-1:
            Command.append("--list-langs")
        elif programOCR[selectionEngineOCRINI].find("Capture2Text_CLI")>-1:
            Command.append("--show-languages")
            bCapture2Text=True
        else:
            Command=["exit"]
        if pathTessdata[selectionEngineOCRINI]:
            Command.append("--tessdata-dir")
            Command.append(pathTessdata[selectionEngineOCRINI])
        process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=PathPlugin)
        output = process.communicate()[0]
        langsOCRTraining = re.split(r"\r\n",output)[1:-1]
        LanguageOCRAvaible = langsOCRTraining if bCapture2Text else filter(None, [LanguagesOCR.get(x) for x in langsOCRTraining] )
#https://github.com/tesseract-ocr/tessdata For Tesseract-OCR4
#https://github.com/tesseract-ocr/tessdata/tree/3.04.00 For Tesseract-OCR3 Capture2Text


def valueDictionary(dictionary,valuetofind):
    v = [key for key, value in dictionary.items() if value.upper() == valuetofind.upper()]
    if len(v)>0:
        return v[0]
    else:
        return ""
def changeCaseText(text,indexCase):
    if selectionCase[indexCase]=="lowercase":
        return text.lower()
    elif selectionCase[indexCase]=="UPPERCASE":
        return text.upper()
    elif selectionCase[indexCase]=="Capitalize":
        return text.capitalize()
    elif selectionCase[indexCase]=="Sentence":
        return re.sub(r"(^|[?!.] )(\w)",lambda x:x.group(0).upper(),text.lower())
    else:
        return text
def BallonForText(Img, Drawable,indexSelectionOCR,indexEngineOCR,bHocr,indexLanguageOCR,oOrientation,bLineBreak,option_CaseOCR,bTranslation,option_CaseTranslation,indexLanTrans,typeFont,colorFont,nameDocument,pathProyect_,indexEditText,bMessage):
    global g_imageActive,g_activeLayer,LayerGroup,pathProyect,g_pathProyectWeb,g_SelectionOCR,g_typeFont,g_sizeFont,g_colorFont,g_nameDocument
    bEditText=False
    g_typeFont=typeFont
    g_colorFont=colorFont
    g_sizeFont=28
    g_SelectionOCR = SelectionOCR[indexSelectionOCR]
    selectionEdit = SELECTIONEDIT[indexEditText]
    nameLayers =[]
    pathImagesOCR=[]
    pathProyect = pathProyect_ + sep
    g_nameDocument = nameDocument
    g_pathProyectWeb = pathProyect + g_nameDocument + sep
    g_imageActive = gimp.image_list()[0] #get imageActive gimp active
    g_activeLayer = pdb.gimp_image_get_active_layer(g_imageActive) #get layer selected
   
    if g_SelectionOCR == "OCR All layers/Path":
        num_vectors, vector_ids = pdb.gimp_image_get_vectors(g_imageActive)
        if num_vectors==0:
            pdb.gimp_message("Not found Paths/Curves")
            return
    elif g_SelectionOCR == "OCR Selection":
        if not pdb.gimp_item_is_layer(g_activeLayer) or pdb.gimp_item_is_group(g_activeLayer) or pdb.gimp_item_is_text_layer(g_activeLayer) or pdb.gimp_selection_is_empty(g_imageActive):
            pdb.gimp_message('Select an layer and make a selection')
            return
    elif g_SelectionOCR == "Update Language":    
        saveFileINI(indexEngineOCR)
        return
    elif g_SelectionOCR == "Only Edit Text":
        gimp.progress_init("PROCESSING Names")
        for r, d, f  in os.walk(g_pathProyectWeb):
            for file in f:
                if os.path.splitext(file)[1] == EXTENSIONOCR:
                    pathImageRelativeExported = os.path.join(os.path.basename(r),file)
                    pathImageRelativeExportedEncHTML=urllib.pathname2url(pathImageRelativeExported.encode("UTF-8"))
                    pathImagesOCR.append(pathImageRelativeExportedEncHTML)
                    pdb.gimp_progress_pulse()
        nameLayers = obtainNamesLayers(1)#all layers/curves
        pdb.gimp_progress_end()
    pdb.gimp_image_undo_group_start(g_imageActive)
    if g_SelectionOCR in ["OCR Selection","OCR All layers/Path"]:
        #Remove holes selection
        pdb.gimp_selection_flood(g_imageActive)
        #Selection to Path
        if not pdb.gimp_selection_is_empty(g_imageActive):
            pdb.plug_in_sel2path(g_imageActive,None)
        # Obtain Layes for process (Path/Curves or selection)
        nameLayers = obtainNamesLayers(indexSelectionOCR)
        gimp.progress_init("PROCESSING GROUPS")
        for nameLayer in nameLayers:
            olayer = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayer)
            layerGroup = pdb.gimp_item_get_parent(olayer)
            if layerGroup==None:
                layerGroup = pdb.gimp_layer_group_new(g_imageActive)
                layerGroup.name = TAGPREFIXGROUP + olayer.name
                g_imageActive.add_layer(layerGroup,0)
                pdb.gimp_image_reorder_item(g_imageActive,olayer,layerGroup,0)
            pdb.gimp_progress_pulse()
        pdb.gimp_progress_end()
    

        gimp.progress_init("EXPORTING IMAGES/PATHS")
        
        threads = list()
        for nameLayer in nameLayers:
            oVector = pdb.gimp_image_get_vectors_by_name(g_imageActive, TAGPATHSTROKE + nameLayer)
            if oVector is None: continue
            num_strokes, stroke_ids = pdb.gimp_vectors_get_strokes(oVector)
            for idStroke in stroke_ids:
                pdb.gimp_selection_none(g_imageActive)
                type, num_points, controlpoints, closed = pdb.gimp_vectors_stroke_get_points(oVector, idStroke)
                vBuffer = pdb.gimp_vectors_new(g_imageActive, "Buffer")
                stroke_id = pdb.gimp_vectors_stroke_new_from_points(vBuffer, type, num_points, controlpoints, closed)
                controlpointsXYSelection= list( zip(controlpoints[2::6], controlpoints[3::6]) )
                pdb.gimp_image_insert_vectors(g_imageActive, vBuffer, None, 0)
                pdb.gimp_image_select_item(g_imageActive, 2, vBuffer)
                #Export image
                pathImageRelativeExported = exportImageSelectioned(nameLayer)
                fileImageForOCR = pathProyect  + g_nameDocument  + sep + pathImageRelativeExported
                tOCR = threading.Thread(target=OCRText, args=( fileImageForOCR,indexEngineOCR,indexLanguageOCR,bHocr,oOrientation,bLineBreak,option_CaseOCR,bMessage,controlpointsXYSelection  ) )
                threads.append(tOCR)
                tOCR.start()
                
                if pathImageRelativeExported is not None:
                    pathImageRelativeExportedEncHTML=urllib.pathname2url(pathImageRelativeExported.encode("UTF-8"))
                    pathImagesOCR.append(pathImageRelativeExportedEncHTML)
                pdb.gimp_progress_pulse()
                pdb.gimp_image_remove_vectors(g_imageActive, vBuffer)
        for tOCR in threads:
            tOCR.join()
            
        pdb.gimp_progress_end()

        pdb.gimp_selection_none(g_imageActive)
        pdb.gimp_image_set_active_layer(g_imageActive, g_activeLayer)
        num_vectors, vector_ids = pdb.gimp_image_get_vectors(g_imageActive)

            
        if bTranslation:
            gimp.progress_init("PROCESSING TRANSLATION")
            destLanguage = languagueCode.items()[indexLanTrans][0]
            for nameLayer in nameLayers:
                filterFilesTXTOCR = g_pathProyectWeb + nameLayer + sep + u"*OcrImage.txt"
                for fileImageForTranslation in glob.glob(filterFilesTXTOCR):
                    Translate(fileImageForTranslation,destLanguage,option_CaseTranslation,bMessage)
                    pdb.gimp_progress_pulse()
            pdb.gimp_progress_end()    

    generateListImageJS (pathImagesOCR)
    editOCR(selectionEdit, indexLanguageOCR,indexLanTrans,option_CaseTranslation,bMessage)
    
        
    bLoadTranslation=False
    if os.path.exists(g_pathProyectWeb + OK):
        os.remove(g_pathProyectWeb + OK)
        bLoadTranslation = True

    if bLoadTranslation ==True:
        gimp.progress_init("LOADING TRANSLATION")
        for nameLayer in nameLayers:
            filterFilesTranslation = g_pathProyectWeb + nameLayer + sep + u"*-T.txt"
            for fileTranslated in glob.glob(filterFilesTranslation):
                loadText(fileTranslated)
                pdb.gimp_progress_pulse()
        pdb.gimp_progress_end()  

    if g_activeLayer is not None:
        pdb.gimp_image_set_active_layer(g_imageActive, g_activeLayer)       
    pdb.gimp_image_undo_group_end(g_imageActive)
    saveFileINI(indexEngineOCR)
    return
def generateListImageJS(pathImagesOCR):
    varJS = u"var listImageOCR = ['{}']".format(  "','".join(pathImagesOCR)  )
    WriteFileUTF(pathProyect  + g_nameDocument + sep + "ListFilesImage.js",varJS)
def obtainNamesLayers(selection):
    # 0 Layer selected
    # 1 All layers/Curves 
    
    num_vectors, vector_ids = pdb.gimp_image_get_vectors(g_imageActive)
    nameLayers =[]
    #find layers name = PathStroke _PS_Name
    for idVector in vector_ids:
        oVector = gimp._id2vectors(idVector)
        if oVector is None: continue
        if oVector.name.find(TAGPATHSTROKE)==0:
            nameLayerPath = oVector.name.replace(TAGPATHSTROKE,"")
        else:
            #rename all path stroke
            oVectorOld= pdb.gimp_image_get_vectors_by_name(g_imageActive, TAGPATHSTROKE + g_activeLayer.name)
            if oVectorOld is not None:
                pdb.gimp_image_remove_vectors(g_imageActive, oVectorOld)
            #rename Path Stroke
            oVector.name = TAGPATHSTROKE + g_activeLayer.name
            nameLayerPath = g_activeLayer.name
        layer = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayerPath) 
        if layer is None:
            continue
        if selection==0 and nameLayerPath == g_activeLayer.name:
            nameLayers = [nameLayerPath]
        elif selection==1:
            if nameLayerPath in nameLayers:
                continue
            else:
                nameLayers.append(nameLayerPath)
    return nameLayers
def applyInfoText(textTranslation,nameLayerBallonEmpty,fileInfo):
        text = ReadFileUTF(fileInfo)
        font_size=28
        # layerBalloonEmpty.
        layerBalloonEmpty = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayerBallonEmpty)
        if not layerBalloonEmpty:
            pdb.gimp_message("Not Found Layer:{}".format(nameLayerBallonEmpty) )
            return
        pdb.gimp_image_set_active_layer(g_imageActive, layerBalloonEmpty)
        layerGroup = pdb.gimp_item_get_parent(layerBalloonEmpty)
        cXb1, cYb1 = layerBalloonEmpty.offsets# Balloon Empty
        cXb2 = cXb1 + layerBalloonEmpty.width
        cYb2 = cYb1 + layerBalloonEmpty.height
        
        cXTxt1=cXb1
        cYTxt1=cYb1
        cXTxt2=cXb2
        cYTxt2=cYb2
        
        #position image OCR (PARENT)
        # coordXY=re.findall("(\d+)\.\d+, (\d+)\.\d+",text)
        b = re.search("bbox_(\d+)_(\d+)_(\d+)_(\d+)",text)#coord local BOX text OCR(Tesseract)
        if b is not None:
            x1,y1,x2,y2 = b.groups()
            x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)#coord local BOX text
            x1G,y1G,x2G,y2G = cXb1+x1, cYb1+y1, cXb1+x2, cYb1+y2 #coord global/Imagen Full
            cXTxt1=x1G
            cYTxt1=y1G
            #for ajust position, pendient
            # xleft = max([int(x) for x,y in coordXY if int(x)<x1G])
            # yleft = min([int(y) for x,y in coordXY if int(y)>y1G])
            # xright = min([int(x) for x,y in coordXY if int(x)>x2G])
            # yright = max([int(y) for x,y in coordXY if int(y)<y2G])

        f = re.search("fn_(\d+)",text)
        if f is not None:
            font_size = int(f.groups()[0])
        
        
        nameLayerText = layerBalloonEmpty.name + "_TEXT"
        layerText = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayerText)
        if not layerText:
            layerText = addLayerText(nameLayerText,font_size,cXTxt1,cYTxt1,cXTxt2,cYTxt2,layerGroup)
        pdb.gimp_text_layer_set_text(layerText, textTranslation)
        
            
def loadText(fileTranslated):
    pattern = "(" + BText + ".*?)_OcrImage"   
    m = re.search(pattern,fileTranslated) #FIND BText###_
    if m:
        nameLayerBallonEmpty = m.group(1)
        textTranslation = ReadFileUTF(fileTranslated)
        if(textTranslation==""):
            textTranslation = "NOT OCR/TRANSLATION"
        
        # if layerText is not None:
        applyInfoText(textTranslation,nameLayerBallonEmpty,fileTranslated.replace("-T.txt",".info"))
    
def exportImageSelectioned(nameLayer):
    #activeLayer is layer active for path 
    colorBalloon = (255,255,255)
    activeLayer = pdb.gimp_image_get_layer_by_name(g_imageActive, nameLayer)
    layerGroup = pdb.gimp_image_get_layer_by_name(g_imageActive, TAGPREFIXGROUP + nameLayer)
    if activeLayer is not None:
        pdb.gimp_image_set_active_layer(g_imageActive, activeLayer)
    else:
        pdb.gimp_message("Not found layer: " + nameLayer)
        return ""
    #get color Balloon Dialogue
    non_empty, Coordx1, Coordy1, Coordx2, Coordy2 = pdb.gimp_selection_bounds(g_imageActive)
    try:
        xColor, yColor = getColor(g_imageActive, Coordx1, Coordy1, Coordx2, Coordy2)
    except Exception as e:
        pdb.gimp_message("Error getColor:"  + str(traceback.format_exc()) +  str(Coordx1) + str(Coordy1) + str(Coordx2) + str(Coordy2))   
        
    try:        
        colorBalloon = pdb.gimp_image_pick_color(g_imageActive, activeLayer, xColor, yColor, False, False, 0)
    except Exception as e:
        pdb.gimp_message("Error image_pick_color:%s \r\n %s"%(activeLayer.name, str(e))) 
        
    # pdb.gimp_edit_copy_visible(g_imageActive)
    #ADD BACKGROUND TO IMAGE FOR OCR AND FOR GLOBE TEXT EMPTY TO IMAGE
    pdb.gimp_edit_copy(activeLayer)
    ImageSelection=pdb.gimp_edit_paste_as_new_image()
    layer_GlobeText = pdb.gimp_layer_new_from_drawable(ImageSelection.layers[0], g_imageActive)
    layer_GlobeText.name = BText + "_"+ unicode(activeLayer.name) #Name Baloon Text
    pdb.gimp_image_insert_layer(g_imageActive, layer_GlobeText, layerGroup, 0)
    colorBackup = pdb.gimp_context_get_background()
    pdb.gimp_context_set_background(colorBalloon)
    # pdb.gimp_layer_set_lock_alpha(layer_GlobeText, True)
    #set color background of Ballon (frame-square)
    layer_Background = pdb.gimp_layer_copy(ImageSelection.layers[0], False)
    pdb.gimp_drawable_fill(layer_Background, FILL_BACKGROUND)
    pdb.gimp_image_insert_layer(ImageSelection, layer_Background, None, 1)
    LayerMerge = pdb.gimp_image_merge_visible_layers(ImageSelection, CLIP_TO_IMAGE)

    #EXPORT IMAGE
    PathT = pathProyect  + g_nameDocument
    pathImageRelative = activeLayer.name + sep +  layer_GlobeText.name + "_"+ nameFileImageOCR
    pathImageOCR = PathT + sep + pathImageRelative
    
    try:
        if not os.path.exists(os.path.dirname(pathImageOCR)):
            os.makedirs(os.path.dirname(pathImageOCR))    
        pdb.gimp_file_save(ImageSelection,LayerMerge,pathImageOCR,nameFileImageOCR)
    except Exception as e:
        pdb.gimp_message("Error save image exported" + pathImageOCR + " : \r\n" + str(traceback.format_exc()))
        return None
    pdb.gimp_layer_set_offsets(layer_GlobeText, Coordx1, Coordy1)
    pdb.gimp_drawable_edit_fill(layer_GlobeText, FILL_BACKGROUND)
    pdb.gimp_context_set_background(colorBackup)
    pdb.gimp_image_delete(ImageSelection)
    return pathImageRelative
def addLayerText(nameLayerText,font_size, Coordx1,Coordy1,Coordx2,Coordy2,layerGroup):
    #ADD LAYER TEXT
    layerText = pdb.gimp_text_layer_new(g_imageActive,"--IN PROGRESS OCR/TRANSLATION--", g_typeFont, g_sizeFont, 0)
    layerText.name = nameLayerText
    pdb.gimp_image_insert_layer(g_imageActive, layerText, layerGroup, -1)
    pdb.gimp_layer_set_offsets(layerText, Coordx1, Coordy1)
    pdb.gimp_text_layer_resize(layerText, Coordx2-Coordx1, Coordy2-Coordy1)
    pdb.gimp_text_layer_set_color(layerText, g_colorFont)
    pdb.gimp_text_layer_set_justification(layerText, TEXT_JUSTIFY_CENTER)
    pdb.gimp_text_layer_set_font_size(layerText, font_size, PIXELS)
    return layerText
def getColor(g_imageActive, Coordx1, Coordy1, Coordx2, Coordy2):
    for y in range (Coordy1+8,Coordy2,2):
        for x in range(Coordx1+8,Coordx2,2):
            # is in selection
            inArea = pdb.gimp_selection_value(g_imageActive, x, y)
            if (inArea == 255):
                return x,y
    return 0,0

def OCRText(fileImageForOCR, selectionOCR,indexLanguageOCR,bHocr,oOrientation,bLineBreak,option_CaseOCR,bMessage, pointsSelection = [(0,0)] ):# [(0,0),(454,121)...] 
    Command=""
    try:
        if(indexLanguageOCR==-1):
            return "Error:Select a language for OCR"
        fileOCROutput = os.path.splitext(fileImageForOCR)[0]
        fileHocr = fileOCROutput + HOCR
        pdb.gimp_message(fileHocr)
        if os.path.exists(fileHocr):
            os.remove( fileHocr )
        # fileOCROutput = fileImageForOCR.replace(EXTENSIONOCR,"")
        destLanguageOcr = valueDictionary( LanguagesOCR, LanguageOCRAvaible[indexLanguageOCR] )
        destLanguageFullOcr = LanguageOCRAvaible[indexLanguageOCR]
        iOrientation=3 #default for Tesseract
        OrientationVertical=""
        if oOrientation==1:
            iOrientation=6
        elif oOrientation==2:
            iOrientation=5
            OrientationVertical="--vertical"
        delimiter = "|"
        argsCommand=Template(argsOCR[selectionOCR].replace(" ",delimiter)).safe_substitute(\
        PATHTESSDATA=pathTessdata[selectionOCR],\
        NAMEFILEIMAGEOCR=fileImageForOCR,\
        NAMEFILEOUTOCR=fileOCROutput,\
        ORIENTATION=iOrientation,\
        DESTLANGUAGEOCR=destLanguageOcr,\
        DESTLANGUAGEFULLOCR=destLanguageFullOcr,\
        ORIENTATIONVERTICAL = OrientationVertical
        )
        Command = [programOCR[selectionOCR]]
        Command.extend( argsCommand.strip().split(delimiter) )
        if bHocr==False:
            if u"hocr" in Command:
                Command.remove(u"hocr")
        
        process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=PathPlugin)
        output = process.communicate()
        if( process.returncode!=0):
            # fix problems errors training tesseract
            if(output[1].find("IntDotProductSSE")>0):
                Command.insert(-1,"--oem")
                Command.insert(-1,"0")
                process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=PathPlugin)
                output = process.communicate()

        if( process.returncode!=0):
            pdb.gimp_message(str(output[1]))
            return output[1]
        readHOCR(fileOCROutput,pointsSelection)
        OCRText = ReadFileUTF(fileOCROutput+TXT)

        if(bLineBreak):#PENDIENTE PARA CAPTURE TEXT
            OCRText = OCRText.replace("-\r\n", "")#remove guion for conti- nuation
            OCRText = re.sub(r"\s+", " ", OCRText, flags=re.UNICODE)
        
        OCRText = changeCaseText(OCRText,option_CaseOCR)
        OCRText = FixOCR(OCRText)
        if (0):
            subprocess.Popen(['clip'], stdin=subprocess.PIPE).communicate(OCRText.encode("UTF-16"))
        WriteFileUTF(fileOCROutput + TXT,OCRText)
        WriteFileUTF(fileOCROutput + "-T" + TXT,OCRText)
        if bMessage: pdb.gimp_message(fileOCROutput + "\r\n" + OCRText)
    except Exception as e:
        pdb.gimp_message("Error OCR:" + str(traceback.format_exc()) )
        pdb.gimp_message("Error Command:" + str(Command) )
        
def FixOCR(text):
    #FIX TESSERACT 4.1 END FILE
    text = re.sub(r"", "", text, flags=re.UNICODE)
    return text

def Translate(fileOCR,destLanguage,option_CaseTranslation,bMessage):
    ocrTextTo = ReadFileUTF(fileOCR)
    pdb.gimp_progress_set_text('Translation Text Google')
    try:
        from googletrans import Translator
        translator = Translator()
        ToTranslate = translator.translate(ocrTextTo,dest=destLanguage)
        textTranslation = ToTranslate.text
    except Exception as e:
        pdb.gimp_message("Error Translation" + str(traceback.format_exc()) )
        return "Error: Translation"
    textTranslation = changeCaseText(textTranslation,option_CaseTranslation)
    # fix OCR
    textTranslation = textTranslation.replace(" ...","...")
    WriteFileUTF(fileOCR.replace(".txt","-T.txt"),textTranslation)
    if bMessage: pdb.gimp_message(textTranslation)

register(
    "OCRForBalloons",
    "OCR for Dialogue Balloons and Translation of text.",
    "Nothing",
    "Anonymous",
    "-",
    "2019",
    "OCR For Ballons Text",
    "RGB*, GRAY*",
    [
    (PF_IMAGE,"image","Input image", None),
    (PF_DRAWABLE,"drawable", "Input drawable", None),
    (PF_OPTION,"indexSelectionOCR", "OCR/Edit", 0, SelectionOCR),
    (PF_OPTION,"indexEngineOCR", "Type Engine OCR", selectionEngineOCRINI, nameEngineOCR),
    (PF_BOOL,"bhocr","Information position text (HOCR)", True),
    (PF_OPTION,"indexLanguageOCR", "Language OCR/Ballon", 1, LanguageOCRAvaible),
    (PF_OPTION,"oOrientation", "Orientation Text", 0, ("Auto", "Horizontal", "Vertical") ),
    (PF_BOOL,"bLineBreak","Remove Line Break", False),
    (PF_OPTION,"option_CaseOCR", "Change case OCR text", 0,selectionCase),
    (PF_BOOL,"bTranslation","Translation", False),
    (PF_OPTION,"option_CaseTranslation", "Change case Translation", 0,selectionCase),
    (PF_OPTION,"indexLanTrans", "Language For Translation", 7,languagueCode.values()),
    (PF_FONT,"typeFont", "font", "Arial Bold"),
    (PF_COLOUR,"colorFont", "Font color",(0.0, 0.0, 0.0)),
    (PF_STRING,"nameDocument", "Proyect Name", "My Proyect"),
    (PF_DIRNAME,"pathProyect", "Directory ImageOCR", Path),
    (PF_OPTION,"indexEditText", "Edit Text OCR&Translation", 1,SELECTIONEDIT),
    (PF_BOOL,"bMessage","OCR&Translation To Console", False),
    ],
    [],
    BallonForText,
    menu="<Image>/Layer/"
)
def readHOCR(pathFile,pointsSelection):
    OCRText = ""
    size=0
    sizeFont=""
    bbox=""
    lines=""
    if os.path.exists(pathFile + ".hocr"):
        tree = ET.parse(pathFile + ".hocr")
        streamXML = ReadFileUTF(pathFile + ".hocr")
        x_size = re.findall("x_size (\d+)", streamXML, re.U)
        if x_size != []:
            x_size = list(map(lambda x: int(x) , x_size))#convert number unicode [u'1234',] a int [1234,]
            size = sum(x_size)/len(x_size) 
        if size>5:
            sizeFont= "\r\n" + "fn_"+str(size)

        m = re.search("id=.block.*?(bbox \d+ \d+ \d+ \d+)", streamXML, flags=re.IGNORECASE)
        if m :
            bbox =  m.group(1)
            bbox = bbox.replace(" ","_")

        textXML = re.findall(r"<span.*?>(.*?)</span>",streamXML)


        # OCRText = "".join(tree.getroot().itertext())
        root = tree.getroot()
        nameSpace = root.tag.replace("}html","}") #xmlns="http://www.w3.org/1999/xhtml"
        for word in root.iter( nameSpace + 'span'):#required namespace for find class
            if word.get("class")=='ocr_line':
                OCRText = OCRText + CARRIAGERETURN
            else:
                OCRText = OCRText + "".join(word.itertext()) + " " # word.text fail tags aditionals <strong></strong> 
        OCRText = re.sub(r"\s\s+",CARRIAGERETURN,OCRText).strip()
        
        aLines = re.findall("class=.ocr_line.*?(bbox \d+ \d+ \d+ \d+)", streamXML, flags=re.IGNORECASE)
        lines = CARRIAGERETURN + CARRIAGERETURN.join(aLines)
        #fix space start and end
        OCRText = OCRText.strip()
        #fix lines empty (only space)
        OCRText = re.sub("\r\n *\r\n",CARRIAGERETURN,OCRText) 
        #fix &#39; '
        OCRText = HTMLParser.HTMLParser().unescape(OCRText)
        WriteFileUTF(pathFile + TXT,OCRText)
    WriteFileUTF(pathFile + ".info",bbox + sizeFont + lines + CARRIAGERETURN + str(pointsSelection))


class StoreHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        form = cgi.FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'],})
        try:
            for name in form.keys():
                nameFile = g_pathProyectWeb + urllib.url2pathname(name)
                with open(nameFile,"wb") as f:
                    f.write(form[name].value)
            self.respond("OK")
        except Exception as e:
            self.send_error(500,'ERROR:%s %s'%(str(traceback.format_exc()),file) )
            pdb.gimp_message(traceback.format_exc())
        return
    # def do_POST(self):
        # content_length = int(self.headers['Content-Length'])
        # body = self.rfile.read(content_length)
        # self.send_response(200)
        # self.end_headers()
        # response = BytesIO()
        # response.write(b'This is POST request. ')
        # response.write(b'Received: ')
        # response.write(body)
        # self.wfile.write(response.getvalue())
    def do_GET(self):
        curdirok = pathProyect + g_nameDocument
        if self.path=="/":
            self.path=namePageHTML
        try:
            #Check the file extension required and
            #set the right mime type
            sendReply = False
            if self.path.endswith(".html"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".txt"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype='image/jpg'
                sendReply = True
            if self.path.endswith(".ico"):
                mimetype='image/ico'
                sendReply = True
            if self.path.endswith(".png"):
                mimetype='image/png'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype='image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype='text/css'
                sendReply = True
            if sendReply == True:
                #decoding spaces of URL
                selfpath = urllib.url2pathname(self.path)
                #Open the static file requested and send it
                file = g_pathProyectWeb + selfpath
                with open(file,'rb') as f:
                    response = f.read()
                self.respond(response,mimetype,200)
            else:
                self.respond("Unknown request extension",status=404)
        except Exception as e:
            self.send_error(500,'ERROR:%s %s'%(str(e),file) )
    def tryAgain_response(self,status,retries=0):
        if retries > 3:  raise NameError('Error Send Status: %s'%status)
        try:self.send_response(status)
        except: self.tryAgain_response(retries+1)
    def respond(self, response,mimetype="text/html", status=200):
        self.protocol_version = 'HTTP/1.1'
        self.tryAgain_response(status)
        self.send_header("Content-type",mimetype)
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)
        
def webServer():
    import socket;
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((IP,PORT))
    sock.close()
    if result != 0:
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer((IP, PORT), StoreHandler)
        thread = threading.Thread(None, httpd.serve_forever)
        thread.start()
        sCommand=r'start /wait "Title Web" "{program}" {ip}:{port} {options}'.format(program=programWeb[0],ip=IP, port=PORT, options=optionsWeb[0])
        process = subprocess.call(sCommand, shell=True)
        httpd.shutdown()
        httpd.server_close()
        thread.join()
    else:
        pdb.gimp_message( "Error: port in use:{} change a other port".format(PORT) )
def editOCR(selectionEdit, indexLanguageOCR,indexLanTrans,option_CaseTranslation,bMessage):
    outputOCR=""
    translation=""
    # destLanguageOcr = [key for key, value in LanguagesOCR.items() if value == LanguageOCRAvaible[indexLanguageOCR]][0]
    # srcLanguage= "sp" + str(indexLanguageOCR)
    srcLanguage = valueDictionary(languagueCode,LanguageOCRAvaible[indexLanguageOCR])
    destLanguage = languagueCode.items()[indexLanTrans][0]
    HTAFix= sHTA.replace("MyPathFileTranslation",nameFileTranslation)\
    .replace("{LANGUAGESOURCE}",srcLanguage)\
    .replace("{LANGUAGEDESTINY}",destLanguage)\
    .replace("{FLAGTRANSLATIONHTA}",bPathTranslation)\
    .replace("\\","/")
    PathHTA = g_pathProyectWeb + namePageHTML
    WriteFileUTF(PathHTA,HTAFix)
    if  selectionEdit == "Edit HTA/IE":
        Command = ["start","/wait",'mshta',PathHTA]
        for x in range(100):
            process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=g_pathProyectWeb)
            output = process.communicate()
            if os.path.exists(bPathTranslation):
                os.remove(bPathTranslation)
                f = codecs.open(g_pathProyectWeb + nameFileTXTOCR, encoding='utf-8')
                OCRText = f.read()
                f.close()
                translation = Translate(destLanguage,OCRText,option_CaseTranslation,bMessage)
                WriteFileUTF(nameFileTranslation,translation)
            else:
                break
    elif selectionEdit == "Edit WebNavigator":
        webServer()
    elif selectionEdit == "Edit Subtitle(ASS)":
        filePathASS =os.path.join(g_pathProyectWeb,FILEASS)
        filePathAVS =os.path.join(g_pathProyectWeb,FILEAVS)
        editSubtitleAss(filePathASS,filePathAVS)
        timeLastModification = os.path.getmtime(filePathASS)
        Command = ["start","/wait","Title Subtitle",filePathASS]
        subprocess.call(Command,shell=True,cwd=g_pathProyectWeb)
        if os.path.getmtime(filePathASS)>timeLastModification:
            exportTXTSubtitle(filePathASS)
    else:
        return

def editSubtitleAss(filePathASS,filePathAVS):
    #FOR Subtitle Aegisub, and video AVS
    count=0
    fwAss =open(filePathASS,"wb")
    fwAss.write(headAss)
    fwAvs =open(filePathAVS,"wb")
    fwAvs.write(headAVS)

    for r, d, f  in os.walk(g_pathProyectWeb):
        for file in f:
            name,ext = os.path.splitext(file)
            if ext.lower() == EXTENSIONOCR.lower():
                fileOCR = os.path.join(r,name+TXT)
                fileTranslation = os.path.join(r,name + T_TXT)
                textOCR = ReadFileUTF(fileOCR).replace("\r\n",r"\N").replace("\n",r"\N")
                textTranslation = ReadFileUTF(fileTranslation).replace("\r\n",r"\N").replace("\n",r"\N")
                begin = time.strftime("%H:%M:%S", time.gmtime(count))
                end= time.strftime("%H:%M:%S", time.gmtime(count+1))
                sDialogue = r"Dialogue: 0,{}.00,{}.00,{},{}/{},0,0,0,,{}".format(begin,end,"OCR",os.path.basename(r),name,textOCR)
                fwAss.write(sDialogue + "\r\n")
                sDialogue = r"Dialogue: 0,{}.00,{}.00,{},{}/{},0,0,0,,{}".format(begin,end,"Translate",os.path.basename(r),name,textTranslation)
                fwAss.write(sDialogue + "\r\n")
                sImage=r'+ImageOCR("{}{}{}")\ '.format(os.path.basename(r),sep,file)
                fwAvs.write(sImage + "\r\n")
                count+=1
    fwAvs.close()
    fwAss.close()

def exportTXTSubtitle(filePathASS):
    fh = open( filePathASS )
    while True:
        line = fh.readline()
        if not line:
            break
        g = re.search("Dialogue.*?(OCR|Translate),(.*),0,0,0,,(.*)",line)
        if g:
            if (g.group(1)=="Translate"):
                ext=T_TXT
            elif(g.group(1)=="OCR"):
                ext=TXT
            else:
                break
            nameFile = g.group(2)+ext
            contentText = g.group(3).replace(r"\N","\r\n")
            if(contentText!=""):
                WriteFileUTF(os.path.join(g_pathProyectWeb,nameFile),contentText)
        # check if line is not empty
    fh.close()
    WriteFileUTF(os.path.join(g_pathProyectWeb,OK) ,"OK")    
sHTA = """<!DOCTYPE html>
<HTML>
<meta http-equiv="x-ua-compatible" content="ie=9" content="text/html" charset="UTF-8">
<SCRIPT LANGUAGE="javascript">
languageSource = "{LANGUAGESOURCE}"
languageDestiny = "{LANGUAGEDESTINY}"
fileBTMPOCR="{FLAGTRANSLATIONHTA}"
//isHTA=(window.location.protocol!="http:")
var isHTA=(window.external==null)
var aTextAreaOCR = []//Array textArea OCR
var aTextAreaTranslated = []//Array textArea Translated
</SCRIPT>
<script type="text/javascript" src="ListFilesImage.js"></script> 
<HEAD>
   <TITLE>OCR TEXT</TITLE>
   <HTA:APPLICATION
   ID = "oApp"
   APPLICATIONNAME = "OCR TEXT"
   BORDER = "thick"
   CAPTION = "yes"
   SHOWINTASKBAR = "yes"
   SINGLEINSTANCE = "yes"
   SYSMENU = "yes"
   WINDOWSTATE = "normal"
   SCROLL = "yes"
   SCROLLFLAT = "yes"
   VERSION = "1.0"
   INNERBORDER = "yes"
   SELECTION = "yes"
   MAXIMIZEBUTTON = "yes"
   MINIMIZEBUTTON = "yes"
   NAVIGABLE = "yes"
   CONTEXTMENU = "yes"
   BORDERSTYLE = "normal"
   </HTA>
    <style>
    html,body,form {
        
    }
    img{
		height: auto;
        width:100%;
    }
	th, td {
		padding:5px;
	}
	textarea{
			width:100%;
			height:200px;
			autocomplete =on
			spellcheck=true
			autocapitalize =sentences

	}
    #Headers {
      width: 100%;
	  top: 35px;
      background-color: #ddd;
	  position: fixed;
    }
    #myProgress {
      width: 100%;
      background-color: #ddd;
	  position: fixed;
    }
    #myBar {
      width: 0%;
      height: 25px;
      background-color: #4CAF50;
      text-align: center;
      line-height: 30px;
      color: white;
	  font-size:100%;
    }
    </style>

</HEAD>
<BODY>
<form enctype="multipart/form-data" method="post" name="myForm" id="myForm" onsubmit="">
	<table id ="TableImageOCR" border="0" style="width:100%;height:100%">
    <tr>
    <td style="width:100%;height:30px" colspan="4">
    </td>
    </tr>
    <tr>
    <div id="myProgress"><div id="myBar">0%</div>
    </div>
    </tr>
	<tr>
	<td style="height:5%" colspan="3">
	<div id="Headers">
	<button type="button" onclick="SaveFiles()">Accept</button>
	<button type="button" onclick="SaveFiles();SaveFlag();window.close();">Translate</button>
	<button hidden type="button" onclick="closeHTA()">Close</button>
	<button hidden onclick="TranslatorBing()">BING</button>
	<button hidden onclick="TranslatorGoogle()">Google</button>
	<div id='MicrosoftTranslatorWidget' class='Dark' style='color:white;background-color:#555555'></div>
	<div id="google_translate_element"></div>
	</div>
	</td>
	</tr>
	</table>
</form>
<form enctype="multipart/form-data" method="post" name="myFormOK" id="myFormOK" onsubmit="">
<input type="hidden" name="ok.txt" value="ok">
</form>
<SCRIPT language="JavaScript">

window.onload = createRowsForImageOCR;
iterationDiv = 0
function createRowsForImageOCR()
{
    
	var cols = 4;
	var table = document.getElementById("TableImageOCR")
	for (i = 0; i < listImageOCR.length; i++)
	{
	  nameFileImage=listImageOCR[i] 
	  var row = document.createElement("tr");
	  var divHiddenTranslate = document.createElement("pre");
	  divHiddenTranslate.style = "color:white;width:0px;height:0px;font-size:0px;"
	  for (var c = 0; c < cols; c++) {
		var cell = document.createElement("td");
		if (c==0 || c==2)
		{
			child = document.createElement("textarea");
			child.method = "post"
			child.lang=languageSource
			if (c==0)//AREA TEXT OCR/SOURCE
			{
				nameFileText = nameFileImage.substr(0, nameFileImage.lastIndexOf(".")) + ".txt"
				sText = readFileText(nameFileText)
				child.name = nameFileText
				child.value = sText;
				aTextAreaOCR.push(child)

				divHiddenTranslate.innerHTML = sText;
				child.addEventListener("keydown", areaTextListenerSource(divHiddenTranslate,child))
			}
			if (c==2)//AREA TEXT TRANSLATED
			{
				nameFileText = nameFileImage.substr(0, nameFileImage.lastIndexOf(".")) + "-T.txt"
				sText = readFileText(nameFileText)
				child.name=nameFileText
				child.lang=languageDestiny
				child.value = sText;
				aTextAreaTranslated.push(child)

				//observe change in div hidden(made translator) for put areatext
				divListenerSource(divHiddenTranslate,child)
			}
		}
		else if(c==1)
		{	
			child = document.createElement("img");
			child.src = nameFileImage;
            child.alt=nameFileImage;
			child.style = "width:auto;height:auto"
		}
		
		if (c==3 && !isHTA)
		{
			cell.appendChild(divHiddenTranslate)//Div hidden for translator(Google,Bing,Yandex)
		}
		else
		{
			cell.appendChild(child);
		}
			row.appendChild(cell)
	  }
	  table.appendChild(row);
	}
	
}

function areaTextListenerSource(oDivHidden,oAreaTextSource)
{
	var timer = 0;
	return function(){
		clearTimeout(timer);
		timer = setTimeout(  function(){oDivHidden.innerHTML = oAreaTextSource.value},1000);
	}

}
function divListenerSource(oDivHidden,oAreaTextObjetive)
{
    var elem = document.getElementById("myBar");  
    var width = 10;
	if ("MutationObserver" in window)
	{
		var observer = new MutationObserver( function(mutations){
        oAreaTextObjetive.value = mutations[0].target.innerText
        iterationDiv++
        width= (iterationDiv/listImageOCR.length*100).toFixed(2)
        elem.style.width = (width>100?100:width) + '%'; 
        elem.innerHTML = width * 1  + '%';
        } );
		var config = { attributes: true, childList: true, characterData: true }
		observer.observe(oDivHidden, config);
	}
}


function readFileText(fileTxt)
{
	sText = "";
	if(isHTA)
	{
		var adTypeText = 2;
		var stream = new ActiveXObject("ADODB.Stream");
		stream.Type = adTypeText;
		stream.Charset = "utf-8";
		stream.Open();
		stream.LoadFromFile(decodeURIComponent(fileTxt));
		sText = stream.ReadText();
		stream.close();
	}
	else
	{
		var client = new XMLHttpRequest();
		client.open('GET',fileTxt,false);
		try
		{
			client.send(null);
			//if(client.status === 200)
			sText = client.responseText
		}
		catch(error)
		{
			sText = error;
		}
	}
	return sText
}
   
function SaveFlag()
{
    writeFilelocal(fileBTMPOCR,"");
}

function writeFilelocal(file,data)
{
    if (data=="")
		return;//Error is empty to write
    var adTypeBinary = 1;
    var adTypeText = 2;
    var adSaveCreateOverwrite = 2;
    var stream = new ActiveXObject("ADODB.Stream");
    stream.Type = adTypeText;
    stream.Charset = "utf-8";
    stream.Open();
    stream.WriteText(data);
    stream.SaveToFile(file, 2);
    stream.close();
}
function SaveFiles()
{
  if(isHTA)
  {
	for (i=0;i<aTextAreaTranslated.length;i++)
	{
		try
		{
			writeFilelocal( decodeURIComponent(aTextAreaTranslated[i].name), aTextAreaTranslated[i].value );
			writeFilelocal( decodeURIComponent(aTextAreaOCR[i].name), aTextAreaOCR[i].value );
		}
		catch(error)
		{
			alert("Error save File:" + error)
			break;
		}
	}
    writeFilelocal( "ok.txt", "ok" );//Flag Ok
    window.close();
  }
  else
  {
	//document.getElementById("myForm").submit();
	submitForm(document.getElementById("myForm"));
	submitForm(document.getElementById("myFormOK"));
    
  }
}
function submitForm(oFormElement)
{
  var xhr = new XMLHttpRequest();
  xhr.onload = function(){if(xhr.status==200) window.close(); else alert(xhr.responseText); } // success case
  xhr.onerror = function(){ alert("Error save file :" + xhr.responseText); } // failure case
  xhr.open (oFormElement.method, oFormElement.action, true);
  xhr.send (new FormData (oFormElement));
  return false;
}
function closeHTA()
{
	close();
}

function TranslatorBing(){
	var s=document.createElement('script');
	s.type='text/javascript';s.charset='UTF-8';
	s.src=((location && location.href && location.href.indexOf('https') == 0)?'https://ssl.microsofttranslator.com':'http://www.microsofttranslator.com')+'/ajax/v3/WidgetV3.ashx?siteData=ueOIGRSKkd965FeEGM5JtQ**&ctf=False&ui=true&settings=undefined&from=en&to=de';
	var p=document.getElementsByTagName('head')[0]||document.documentElement;
	p.insertBefore(s,p.firstChild);
}

function googleTranslateElementInit(){
	new google.translate.TranslateElement({pageLanguage: 'en'}, 'google_translate_element');
}

function TranslatorGoogle()
{
	var s=document.createElement('script');
	s.type='text/javascript';s.charset='UTF-8';
	s.src="http://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"
	var p=document.getElementsByTagName('head')[0]||document.documentElement;
	p.insertBefore(s,p.firstChild);
}

</SCRIPT>
</BODY>
</HTML>
"""
headAss = """[Script Info]
; Script generated by Aegisub 3.2.2
; http://www.aegisub.org/
PlayResX: 640
PlayResY: 480
YCbCr Matrix: None
WrapStyle: 0
ScaledBorderAndShadow: no

[Aegisub Project Garbage]
Last Style Storage: Default
Video File: video.avs
Video AR Value: 1

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Translate,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,9,10,10,10,1
Style: OCR,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,3,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
headAVS="""
global Width=640
global Height=480
global fps=24
global AspectGlobal =  1.0*Width/Height
function ImageOCR (name)
{
   c=ImageReader(name, start=0, end=23, fps=fps)
   Global AspectImage=1.0*c.Width/c.Height
   Img= ( AspectImage>=AspectGlobal  ) ?  c.BilinearResize(Width,int(Width/AspectImage)) : c.BilinearResize(int(Height*AspectImage),Height)
   BorderLeft=0
   BorderTop=Height-Img.Height
   BorderRight=Width-Img.Width
   BorderBottom=0
   return  Img.AddBorders(BorderLeft, BorderTop, BorderRight, BorderBottom, color=$000000)
}

"""

main()
