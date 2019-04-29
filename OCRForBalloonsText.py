#!/usr/bin/env python
from gimpfu import *
import codecs
import subprocess
import re
import inspect
import sys
import os
import tempfile
Path = tempfile.gettempdir()
#Path Plugin GIMP
PathPlugin = os.path.dirname(inspect.getfile(inspect.currentframe()))
PathSoftwareOCR = PathPlugin + r'\OCR'
# PathSoftwareOCR = r"C:\Program Files\Tesseract-OCR"
PathTraining = PathSoftwareOCR
PathTesseract4 = PathSoftwareOCR + r"\tesseract.exe"    #exe
PathCapture2Text_CLI = PathSoftwareOCR + "\Capture2Text_CLI.exe" #exe
nameFile = "OcrImage"
nameFileImageOCR = nameFile + ".png"
nameFileTXTOCR = nameFile + ".txt"
LanguaguesTranslationGoogle = {
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
if (os.path.isfile(PathTesseract4)):
    process = subprocess.Popen([PathTesseract4,"--list-langs"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=PathTraining)
    output = process.communicate()[0]
    langsOCRTraining = re.split(r"\r\n",output)[1:-1]
    LanguageOCRAvaible =  filter(None, [LanguagesOCR.get(x) for x in langsOCRTraining] ) 
#https://github.com/tesseract-ocr/tessdata For Tesseract-OCR4
#https://github.com/tesseract-ocr/tessdata/tree/3.04.00 For Tesseract-OCR3 Capture2Text



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
def BallonForText(Img, Drawable,bOCR,typeOCR,indexLanguageOCR,oOrientation,bLineBreak,option_CaseOCR,bTranslation,option_CaseTranslation,indexLanTrans,typeFont,sizeFont,colorFont,Capture_Dir,bCopyClipboard,bEditText,bMessage):
    Capture_Dir = Capture_Dir + r"\\"
    image = gimp.image_list()[0] #get image gimp active
    active_layer = pdb.gimp_image_get_active_layer(image) #get layer selected
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
    # pdb.gimp_edit_copy_visible(image)
    pdb.gimp_edit_copy(active_layer)
    ImageSelection=pdb.gimp_edit_paste_as_new_image()
    layer_GlobeText = pdb.gimp_layer_new_from_drawable(ImageSelection.layers[0], image)
    layer_GlobeText.name = "BText"
    outputOCR=""
    textTranslation="empty"
    colorBackup = pdb.gimp_context_get_background()
    pdb.gimp_context_set_background(colorBalloon)
    pdb.gimp_layer_set_lock_alpha(layer_GlobeText, True)
    pdb.gimp_image_insert_layer(image, layer_GlobeText, LayerGroup, 0)
    NameLayerBalloonText = layer_GlobeText.name
    if bOCR:
        #set color background of Ballon (frame-square)
        layer_Background = pdb.gimp_layer_copy(ImageSelection.layers[0], False)
        pdb.gimp_drawable_fill(layer_Background, FILL_BACKGROUND)
        pdb.gimp_image_insert_layer(ImageSelection, layer_Background, None, 1)
        LayerMerge = pdb.gimp_image_merge_visible_layers(ImageSelection, CLIP_TO_IMAGE)
        pdb.gimp_file_save(ImageSelection,LayerMerge,Capture_Dir + nameFileImageOCR,nameFileImageOCR)
        outputOCR = OCRText(typeOCR,indexLanguageOCR,bCopyClipboard,oOrientation,bLineBreak,Capture_Dir,option_CaseOCR,bMessage)
        if bMessage: pdb.gimp_message(NameLayerBalloonText + "\r\n" + outputOCR)
        if bTranslation:
            textTranslation = Translate(indexLanTrans,outputOCR,option_CaseTranslation,bMessage)
            if bMessage: pdb.gimp_message(NameLayerBalloonText + "\r\n" + textTranslation)
        else:
            textTranslation = outputOCR
        if(bEditText):
            textTranslation = editHTA(Capture_Dir,outputOCR,textTranslation,indexLanTrans,option_CaseTranslation,bMessage)
    pdb.gimp_image_delete(ImageSelection)
    layertext = pdb.gimp_text_layer_new(image,textTranslation, typeFont, sizeFont, 0)
    layertext.name = NameLayerBalloonText + "_" + layertext.name
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
    for y in range (Coordy1+5,Coordy2,5):
        for x in range(Coordx1+5,Coordx2,5):
            # is in selection
            inArea = pdb.gimp_selection_value(image, x, y)
            if (inArea == 255):
                return x,y
    return 0,0           

def OCRText(typeOCR,indexLanguageOCR,bCopyClipboard,oOrientation,bLineBreak,Capture_Dir,option_CaseOCR,bMessage):
    if typeOCR==1:
        destLanguageOcr = LanguageOCRAvaible[indexLanguageOCR]
        Command = [PathCapture2Text_CLI]
        Command.append("-l")
        Command.append(destLanguageOcr)
        Command.append("-i")
        Command.append(Capture_Dir + nameFileImageOCR)
        Command.append("-o")
        Command.append(Capture_Dir + nameFileTXTOCR)
        if(not bLineBreak):
            Command.append("-b")
        if (bCopyClipboard):
            Command.append("--clipboard")#It does not work with Japanese
        if oOrientation==2:
            Command.append("-t")
        process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=PathTraining)
        output = process.communicate() 
        if( process.returncode!=0):
            pdb.gimp_message(str(output[1]))
            return "Error"
        OCRText=output[0]
    else:
        destLanguageOcr = [key for key, value in LanguagesOCR.items() if value == LanguageOCRAvaible[indexLanguageOCR]][0]
        Command = [PathTesseract4]
        Command.append("-l")
        Command.append(destLanguageOcr)
        if oOrientation==1:
            Command.append("-psm")
            Command.append("6")
        if oOrientation==2:
            Command.append("-psm")
            Command.append("5")
        Command.append(Capture_Dir + nameFileImageOCR)
        Command.append(Capture_Dir + nameFile)
        process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=PathTraining)
        output = process.communicate()
        if( process.returncode!=0):
            # fix problems errors training tesseract
            if(output[1].find("IntDotProductSSE")>0):
                Command.append("--oem")
                Command.append("0")
                pdb.gimp_message("oem")
                process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=PathTraining)
                output = process.communicate()
            
        if( process.returncode!=0):
            pdb.gimp_message(str(output[1]))
            return output[1]
            
        f = codecs.open(Capture_Dir + nameFileTXTOCR, encoding='utf-8')
        OCRText = f.read()
        if(bLineBreak):
            OCRText = OCRText.replace("-\n", "")
            OCRText = OCRText.replace("-\r\n", "")
            OCRText = re.sub(r"\s+", " ", OCRText, flags=re.UNICODE)
    OCRText = changeCaseText(OCRText,option_CaseOCR)
    OCRText = FixOCR(OCRText)
    if (bCopyClipboard):
            subprocess.Popen(['clip'], stdin=subprocess.PIPE).communicate(OCRText.encode("UTF-16"))
        
    
    return OCRText

def FixOCR(text):
    #FIX TESSERACT 4.1 END FILE
    text = re.sub(r"", "", text, flags=re.UNICODE)
    return text

def Translate(indexLanTrans,ocrTextTo,option_CaseTranslation,bMessage):
    destLa = LanguaguesTranslationGoogle.items()[indexLanTrans][0]
    pdb.gimp_progress_set_text('Translation Text Google')
    from googletrans import Translator
    translator = Translator()
    ToTranslate = translator.translate(ocrTextTo,dest=destLa)
    textTranslation = changeCaseText(ToTranslate.text,option_CaseTranslation) 
    textTranslation = textTranslation.replace(" ...","...")
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
        
        (PF_OPTION, "typeOCR", "Type Engine OCR", 0,
            ("Tesseract 4", "CaptureText")
        ), 
        
        (PF_OPTION, "indexLanguageOCR", "Language OCR/Ballon", 1,
            LanguageOCRAvaible
         ),
        (PF_OPTION, "oOrientation", "Orientation Text", 0,
            ("Auto", "Horizontal", "Vertical")
        ),
        (PF_BOOL,"bLineBreak","Remove Line Break", False),
        (PF_OPTION, "option_CaseOCR", "Change case OCR text", 0,selectionCase),
        (PF_BOOL,"bTranslation","Translation", True),
        (PF_OPTION, "option_CaseTranslation", "Change case OCR text", 0,selectionCase),
        (PF_OPTION, "indexLanTrans", "To Language Translation", 7,
            LanguaguesTranslationGoogle.values()
         ),
        (PF_FONT, "typeFont", "font", "Arial Bold"),
        (PF_ADJUSTMENT, "sizeFont", "Size Font", 32, (1, 100, 1)),
        (PF_COLOUR, "colorFont", "Font color",(0.0, 0.0, 0.0)),
        (PF_DIRNAME, "Capture_Dir", "Directory ImageOCR", Path),
        (PF_BOOL,   "bCopyClipboard", "Copy Text OCR to Clipboard", True),
        (PF_BOOL,   "bEditText", "Edit Text OCR&Translation", False),
        (PF_BOOL,"bMessage","OCR&Translation To Console", False),
    ],
    [],
    BallonForText,
    menu="<Image>/Layer/"
)
def WriteFileUTF(Path,Text):
    f = codecs.open(Path,"w", encoding='utf-8')
    f.write(Text)
    f.close()   
def ReadFileUTF(Path):
    f = codecs.open(Path, encoding='utf-8')
    Text = f.read()
    f.close()   
    return Text
def editHTA(Capture_Dir,outputOCR,translation,indexLanTrans,option_CaseTranslation,bMessage):
    nameFileTranslation = Capture_Dir + nameFile+"_Translation.txt"
    bPathTranslation = Capture_Dir +"BTranslation"
    HTAFix= sHTA.replace("MyPathFileTranslation",nameFileTranslation)\
    .replace("MyPathBTempOCR",bPathTranslation)\
    .replace("MyPahfileOCR",Capture_Dir + nameFileTXTOCR)\
    .replace("MyPathfileImageOCR",Capture_Dir + nameFileImageOCR)\
    .replace("\\","/")
    WriteFileUTF(Capture_Dir+nameFileTXTOCR,outputOCR)
    WriteFileUTF(nameFileTranslation,translation)
    
    PathHTA = Capture_Dir + r"\EditOCRText.hta"
    WriteFileUTF(PathHTA,HTAFix)
    Command = ["start","/wait",PathHTA,]
    for x in range(20):
        
        process = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=PathTraining)
        output = process.communicate() 
        if os.path.exists(bPathTranslation):
            os.remove(bPathTranslation)
            f = codecs.open(Capture_Dir + nameFileTXTOCR, encoding='utf-8')
            OCRText = f.read()
            f.close()
            translation = Translate(indexLanTrans,OCRText,option_CaseTranslation,bMessage)
            # pdb.gimp_message(OCRText)
            # pdb.gimp_message(translation)
            WriteFileUTF(nameFileTranslation,translation)
        else:
            break
    
    return ReadFileUTF(nameFileTranslation)
sHTA = """
<!DOCTYPE html>
<HTML>
<meta http-equiv="x-ua-compatible" content="ie=9" content="text/html; charset=UTF-8">
<SCRIPT LANGUAGE="javascript">
fileOCR="MyPahfileOCR"
fileImageOCR="MyPathfileImageOCR"
fileTranslation="MyPathFileTranslation"
fileBTMPOCR="MyPathBTempOCR"
function Window_onLoad(){  // resize to quarter of screen area, centered
   window.resizeTo(screen.availWidth/2,screen.availHeight/2);
   window.moveTo(screen.availWidth/4,screen.availHeight/4);
}
window.onload=Window_onLoad;
</SCRIPT>
<HEAD>
   <TITLE>OCR TEXT</TITLE>
   <HTA:APPLICATION
   ID = "oApp"
   APPLICATIONNAME = "OCR TEXT"
   BORDER = "thick"
   CAPTION = "yes"
   ICON = "app.ico"
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
        height: 100%;
    }
    img{

        width:100%;
    }
    </style>

</HEAD>
<BODY>
<form name="myForm"> 
		<table style="width:100%;height:95%">
		<tr>
		<td style="height:5%"  colspan="2">
		<button type="button" onclick="SaveFile.call(myForm.AreaTranslateText,fileTranslation)">Accept</button> 
		<button type="button" onclick="SaveTextOCR()">Translate</button> 
		<button hidden type="button" onclick="closeHTA()">Close</button> 
		<button hidden onclick="TranslatorBing()">BING</button> 
		<button hidden onclick="TranslatorGoogle()">Google</button> 
		<div id='MicrosoftTranslatorWidget' class='Dark' style='color:white;background-color:#555555'></div>
		<div id="google_translate_element"></div>
		</td>
		</tr>
		
        <tr>
		<td style="width:80%;height:45%" VALIGN = "Top" Align = "Left">
		<textarea name="AreaOCRText" class="skiptranslate" autocomplete="on" spellcheck="true" lang="en" style="width:100%;height:100%"></textarea> 
		</td>
		
        
        <td rowspan="2">
		<img src="" id="OCRImage" style="width:100%;height:auto"/>
		</td>
		</tr>
        
        
		<tr>
		<td style="width:80%;height:45%"  VALIGN = "Top" Align = "Left">
		<textarea name="AreaTranslateText" autocomplete="on" spellcheck="true" lang="en" style="width:100%;height:100%"></textarea> 
		</td>
		</tr>
		
		</table>
  
    </form> 
    <SCRIPT language="JavaScript">
	document.getElementById('OCRImage').src = fileImageOCR
	ReadFile.call(myForm.AreaOCRText,fileOCR)
	ReadFile.call(myForm.AreaTranslateText,fileTranslation)
	
	
	function ReadFile(FileTxt)
	{
	    var adTypeText = 2;
		var stream = new ActiveXObject("ADODB.Stream");
        stream.Type = adTypeText;
        stream.Charset = "utf-8";
        stream.Open();
        stream.LoadFromFile(FileTxt);
		this.value = stream.ReadText();
        stream.close();
	}
    function SaveTextOCR()
    {
		var stream = new ActiveXObject("ADODB.Stream");
		stream.Open();
		stream.WriteText("");
		stream.SaveToFile(fileBTMPOCR, 2);
        SaveFile.call(myForm.AreaOCRText,fileOCR);
        stream.close();
    }
    
      function SaveFile(FileTxt) {
		var adTypeBinary = 1;
		var adTypeText = 2;
		var adSaveCreateOverwrite = 2;
		var stream = new ActiveXObject("ADODB.Stream");
		stream.Type = adTypeText;
		stream.Charset = "utf-8";
		stream.Open();
		stream.WriteText(this.value);
		stream.SaveToFile(FileTxt, 2);
        stream.close();
		close();
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
		};
		function googleTranslateElementInit() {
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
        function reportWindowSize()
        {
          wHeight = window.innerHeight;
          wWidth = window.innerWidth;
          oOCRImage = document.getElementById('OCRImage')
          imgHeight = oOCRImage.naturalHeight 
          imgWidth = oOCRImage.naturalWidth
          if(imgHeight>imgWidth)
          {
              oOCRImage.style.height=(wHeight*0.9) +"px"
              oOCRImage.style.width ="auto"
          }
          else
          {
            oOCRImage.style.width ="100%"
            oOCRImage.style.height="auto"
          }
        }
        window.addEventListener('resize', reportWindowSize);
    </SCRIPT>	
</BODY>
</HTML>
"""
main()
