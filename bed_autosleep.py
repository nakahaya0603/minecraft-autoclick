import numpy as np
import cv2
from PIL import ImageGrab
from PIL import Image
import time
import pyautogui
import pyocr
import os
import ctypes

#####Config#####
#ベッドインを実施するか
sleep_vaild = True

####Config終わり#####
first = True
vaild = False
cnt = 0
cnt_pre = 0
pix_1 = 0
pix_2 = 0
pix_3 = 0
sleep_mode = False
bed_in_flg = False
mojinokori = False
wake_up_time = ""

def pil2cv(image):
    ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        #print('モノクロ')
        pass
    elif new_image.shape[2] == 3:  # カラー
        #print('カラー')
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        #print('透過')
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image

def cv2pil(image):
    ''' OpenCV型 -> PIL型 '''
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image


def sleep_check(text_cut):
    builder = pyocr.builders.TextBuilder(tesseract_layout=6)
    text = tool.image_to_string(cv2pil(text_cut), lang="jpn", builder=builder)
    #print(text)
    text_in = '朝まで時間を' in text
    if text_in == True:
        return True
    else:
        return False
    
def wakeup_check(conv_img):
    time.sleep(1)
    cut = conv_img[70 : 420, 0: 1520]
    builder = pyocr.builders.TextBuilder(tesseract_layout=6)
    text = tool.image_to_string(cv2pil(cut), lang="jpn", builder=builder)
    #print(text)
    text_in = '位置' in text
    if text_in == True:
        return True
    else:
        return False

def bed_in():
    pyautogui.keyDown('shift')
    pyautogui.rightClick()
    pyautogui.rightClick()
    pyautogui.keyUp('shift')

def bed_out():
    pyautogui.mouseDown()
    time.sleep(1)
    pyautogui.mouseUp()

#環境変数「PATH」にTesseract-OCRのパスを設定。
#Windowsの環境変数に設定している場合は不要。
path='C:\\Program Files\\Tesseract-OCR\\'
os.environ['PATH'] = os.environ['PATH'] + path

#pyocrにTesseractを指定する。
pyocr.tesseract.TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

tools = pyocr.get_available_tools()
tool = tools[0]

while(1):
    cnt = cnt + 1
    img = ImageGrab.grab()
    
    # スクリーンショットをMAT型に変換
    conv_img = pil2cv(img)
    text_cut = conv_img[70 : 420, 0: 1520]
    cv2.rectangle(conv_img, (0, 70), (1520, 420), (0, 255, 0), thickness=10)
    if first == True:
        time_1 = time.time()-1000
        
       
    chk = sleep_check(text_cut)
    if wakeup_check(text_cut) == True and bed_in_flg == True:
        time_1 = time.time()
        print("bedout")
        bed_out()
        bed_in_flg = False
        
    if chk == True and time.time() - time_1 > 10:
        print("bedin")
        bed_in()
        bed_in_flg = True

    #cv2.imshow('output', conv_img)
    key =cv2.waitKey(1)
    if key == 27:
        break
    if key == ord('t'):
        vaild = True
    if key == ord('f'):
        vaild = False

    first = False   
    # 終了処理
cv2.destroyAllWindows()