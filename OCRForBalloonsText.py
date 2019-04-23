#!/usr/bin/env python
from gimpfu import *
import codecs
import subprocess
import re
import tempfile
Path = tempfile.gettempdir()
PathTesseract4 = r"C:\Tesseract-OCR4\tesseract.exe"
PathTesseract4Training = r"C:\Tesseract-OCR4\\"
PathCapture2Text_CLI = r"C:\Capture2Text\Capture2Text_CLI.exe"
#https://github.com/tesseract-ocr/tessdata For Tesseract-OCR4
#https://github.com/tesseract-ocr/tessdata/tree/3.04.00 For Tesseract-OCR3 Capture2Text
LanguagesOCR = {
    "jpn": "Japanese",
    "eng": "English",
    "spa": "Spanish", 
    "fra": "French",
    "deu": "German", 
    "kor": "Korean",
    "rus": "Russian",
}
LanguaguesTranslationGoogle = {
    'es': 'spanish',
    'en': 'english',
    'ja': 'japanese',
    'fr': 'french',
    'it': 'italian',
    'nl': 'dutch',
    'ru': 'russian',
    'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)',
    'de': 'german',
    'ko': 'korean',
}
selectionCase = ("none","lowercase", "UPPERCASE", "Capitalize", "Title line")
def changeCaseText(text,indexCase):
    if selectionCase[indexCase]=="lowercase":
        return text.lower()
    elif selectionCase[indexCase]=="UPPERCASE":
        return text.upper()
    elif selectionCase[indexCase]=="Capitalize":
        return text.capitalize()
    elif selectionCase[indexCase]=="Title line":
        return re.sub(r"(^|[?!.] )(\w)",lambda x:x.group(0).upper(),text.lower())
    else:
        return text
def BallonForText(Img, Drawable,bOCR,typeOCR,indexLanguageOCR,oOrientation,bLineBreak,option_CaseOCR,bTranslation,option_CaseTranslation,indexLanTrans,typeFont,sizeFont,colorFont,Capture_Dir,bCopyClipboard,bMessage):
    image = gimp.image_list()[0]
    active_layer = pdb.gimp_image_get_active_layer(image)
    if not pdb.gimp_item_is_layer(active_layer) or pdb.gimp_item_is_group(active_layer) or pdb.gimp_item_is_text_layer(active_layer) or pdb.gimp_selection_is_empty(image):
        pdb.gimp_message('Select an image and make a selection')
        return -1
    pdb.gimp_image_undo_group_start(image)
    LayerGroup = pdb.gimp_item_get_parent(active_layer)
    if (LayerGroup==None):
        LayerGroup = pdb.gimp_layer_group_new(image)
        LayerGroup.name = "G_" + active_layer.name
        image.add_layer(LayerGroup,0)
        pdb.gimp_image_reorder_item(image,active_layer,LayerGroup,0)
    #get color Balloon Dialogue
    non_empty, Coordx1, Coordy1, Coordx2, Coordy2 = pdb.gimp_selection_bounds(image)
    xColor, yColor = getColor(image, Coordx1, Coordy1, Coordx2, Coordy2)
    colorBalloon = pdb.gimp_image_pick_color(image, active_layer, xColor, yColor, False, False, 0)
    #Remove holes selection
    pdb.gimp_selection_flood(image)
    pdb.gimp_edit_copy_visible(image)
    ImageSelection=pdb.gimp_edit_paste_as_new_image()
    layer_GlobeText = pdb.gimp_layer_new_from_drawable(ImageSelection.layers[0], image)
    layer_GlobeText.name = "BalloonText"
    outputOCR=""
    textTranslation="empty"
    colorBackup = pdb.gimp_context_get_background()
    pdb.gimp_context_set_background(colorBalloon)
    if bOCR:
        #set color background of Ballon (frame-square)
        layer_Background = pdb.gimp_layer_copy(ImageSelection.layers[0], False)
        pdb.gimp_drawable_fill(layer_Background, FILL_BACKGROUND)
        pdb.gimp_image_insert_layer(ImageSelection, layer_Background, None, 1)
        LayerMerge = pdb.gimp_image_merge_visible_layers(ImageSelection, CLIP_TO_IMAGE)
        pdb.gimp_file_save(ImageSelection,LayerMerge,Capture_Dir + r"\OcrImage.jpg","OcrImage.jpg")
        outputOCR = OCRText(typeOCR,indexLanguageOCR,bCopyClipboard,oOrientation,bLineBreak,Capture_Dir,option_CaseOCR,bMessage)

        if bTranslation:
            textTranslation = Translate(indexLanTrans,outputOCR,option_CaseTranslation,bMessage)
        else:
            textTranslation = outputOCR
    pdb.gimp_image_delete(ImageSelection)
    pdb.gimp_layer_set_lock_alpha(layer_GlobeText, True)
    pdb.gimp_image_insert_layer(image, layer_GlobeText, LayerGroup, 0)
    layertext = pdb.gimp_text_layer_new(image,textTranslation, typeFont, sizeFont, 0)
    layertext.name = layer_GlobeText.name + "_" + layertext.name
    pdb.gimp_layer_set_offsets(layer_GlobeText, Coordx1, Coordy1)
    pdb.gimp_image_insert_layer(image, layertext, LayerGroup, 0)
    pdb.gimp_layer_set_offsets(layertext, Coordx1, Coordy1)
    pdb.gimp_text_layer_resize(layertext, Coordx2-Coordx1, Coordy2-Coordy1)
    pdb.gimp_text_layer_set_color(layertext, colorFont)
    pdb.gimp_text_layer_set_justification(layertext, TEXT_JUSTIFY_CENTER)
    pdb.gimp_image_set_active_layer(image, layer_GlobeText)
    pdb.gimp_drawable_edit_fill(layer_GlobeText, FILL_BACKGROUND)
    pdb.gimp_context_set_background(colorBackup)
    pdb.gimp_image_set_active_layer(image, active_layer)    
    pdb.gimp_image_undo_group_end(image)

def getColor(image, Coordx1, Coordy1, Coordx2, Coordy2):
    for y in range (Coordy1+5,Coordy2,3):
        for x in range(Coordx1+5,Coordx2,3):
            inArea = pdb.gimp_selection_value(image, x, y)
            if (inArea == 255):
                return x,y
    return 0,0           

def OCRText(typeOCR,indexLanguageOCR,bCopyClipboard,oOrientation,bLineBreak,Capture_Dir,option_CaseOCR,bMessage):
    if typeOCR=="CaptureText":
        destLanguageOcr = LanguagesOCR.items()[indexLanguageOCR][1]
        Command = [PathCapture2Text_CLI]
        Command.append("-l")
        Command.append(destLanguageOcr)
        Command.append("-i")
        Command.append(Capture_Dir + "\OcrImage.jpg")
        Command.append("-o")
        Command.append(Capture_Dir + "\OcrImage.txt")
        if(not bLineBreak):
            Command.append("-b")
        if (bCopyClipboard):
            Command.append("--clipboard")#It does not work with Japanese
        if oOrientation=="Vertical":
            Command.append("-t")
        process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=None, shell=True)
        OCRText = process.communicate()[0]   
    else:
        destLanguageOcr = LanguagesOCR.items()[indexLanguageOCR][0]
        Command = [PathTesseract4]
        Command.append("-l")
        Command.append(destLanguageOcr)
        Command.append(Capture_Dir + "\OcrImage.jpg")
        Command.append(Capture_Dir + "\OcrImage")
        if(destLanguageOcr=="jpn"):
            Command.append("--oem")
            Command.append("0")
        process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=PathTesseract4Training)
        output = process.communicate()
        if( process.returncode!=0):
            pdb.gimp_message(output[1])
            return "Error Capture:"
            
        f = codecs.open(Capture_Dir + r"\OcrImage.txt", encoding='utf-8')
        OCRText = f.read()
        if(bLineBreak):
            OCRText = OCRText.replace("\r\n", " ")
            OCRText = re.sub(r"\s+", " ", OCRText, flags=re.UNICODE)
    OCRText = changeCaseText(OCRText,option_CaseOCR)
    if (bCopyClipboard):
            subprocess.Popen(['clip'], stdin=subprocess.PIPE).communicate(OCRText.encode("UTF-16"))
        
    if bMessage: pdb.gimp_message(OCRText)
    return OCRText


def Translate(indexLanTrans,ocrTextTo,option_CaseTranslation,bMessage):
    destLa = LanguaguesTranslationGoogle.items()[indexLanTrans][0]
    pdb.gimp_progress_set_text('Translation Text Google')
    from googletrans import Translator
    translator = Translator()
    ToTranslate = translator.translate(ocrTextTo,dest=destLa)
    textTranslation = changeCaseText(ToTranslate.text,option_CaseTranslation) 
    if bMessage: pdb.gimp_message(textTranslation)
    return textTranslation


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
        (PF_IMAGE, "image",       "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_BOOL,   "bOCR", "OCR", True),
        
        (PF_RADIO, "typeOCR", "Type Engine OCR", "CaptureText",
            (
                ("CaptureText", "CaptureText"),
                ("Tesseract 4", "Tesseract 4")
            )
        ), 
        
        (PF_OPTION, "indexLanguageOCR", "Language OCR/Ballon", 2,
            LanguagesOCR.values()
         ),
        (PF_RADIO, "oOrientation", "Orientation Text", "Horizontal",
            (
                ("Horizontal", "Horizontal"),
                ("Vertical", "Vertical")
            )
        ),
        (PF_BOOL,"bLineBreak","Remove Line Break", False),
        (PF_OPTION, "option_CaseOCR", "Change case OCR text", 0,selectionCase),
        (PF_BOOL,"bTranslation","Translation", True),
        (PF_OPTION, "option_CaseTranslation", "Change case OCR text", 0,selectionCase),
        (PF_OPTION, "indexLanTrans", "To Language Translation", 5,
            LanguaguesTranslationGoogle.values()
         ),
        (PF_FONT, "typeFont", "font", "Arial Bold"),
        (PF_ADJUSTMENT, "sizeFont", "Size Font", 32, (1, 100, 1)),
        (PF_COLOUR, "colorFont", "Font color",(0.0, 0.0, 0.0)),
        (PF_DIRNAME, "Capture_Dir", "Directory ImageOCR", Path),
        (PF_BOOL,   "bCopyClipboard", "Copy Text OCR to Clipboard", True),
        (PF_BOOL,"bMessage","OCR&Translation To Console", False),
    ],
    [],
    BallonForText,
    menu="<Image>/Layer/"
)

main()