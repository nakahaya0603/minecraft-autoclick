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
sleep_vaild = False

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
    
    ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)

    # マウスイベントの情報
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long),
                    ("dy", ctypes.c_long),
                    ("mouseData", ctypes.c_ulong),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ULONG_PTR)]


    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong),
                    ("mi", MOUSEINPUT)]
        
    LPINPUT = ctypes.POINTER(INPUT)

    SendInput = ctypes.windll.user32.SendInput
    SendInput.argtypes = (ctypes.c_uint, LPINPUT, ctypes.c_int)
    SendInput.restype = ctypes.c_uint

    #右下ベッド
    x, y = 250, 200
    _mi = MOUSEINPUT(x, y, 0, 0x0001, 0, None)
    SendInput(1, INPUT(0, _mi), ctypes.sizeof(INPUT))
    pyautogui.rightClick()

def bed_out():
    ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)

    # マウスイベントの情報
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long),
                    ("dy", ctypes.c_long),
                    ("mouseData", ctypes.c_ulong),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ULONG_PTR)]


    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong),
                    ("mi", MOUSEINPUT)]
        
    LPINPUT = ctypes.POINTER(INPUT)

    SendInput = ctypes.windll.user32.SendInput
    SendInput.argtypes = (ctypes.c_uint, LPINPUT, ctypes.c_int)
    SendInput.restype = ctypes.c_uint
    
    x, y = -250, -200
    _mi = MOUSEINPUT(x, y, 0, 0x0001, 0, None)
    SendInput(1, INPUT(0, _mi), ctypes.sizeof(INPUT))

def turi_mode(conv_img,time_1,time_2):
    click = False
    global cnt_pre
    global pix_1
    global pix_2
    global pix_3
    global sleep_mode
    
    #1080p
    #cnv_cut = conv_img[950/2 : 1450/2, 1750/2: 2120/2]
    #cv2.rectangle(conv_img, (1750/2, 950/2), (2120/2, 1450/2), (0, 255, 0), thickness=10)
    
    #4K
    cnv_cut = conv_img[950 : 1450, 1750: 2120]
    cv2.rectangle(conv_img, (1750, 950), (2120, 1450), (0, 255, 0), thickness=10)
    
    text_cut = conv_img[70 : 420, 0: 1520]
    cv2.rectangle(conv_img, (0, 70), (1520, 420), (0, 255, 0), thickness=10)
    
    hsv = cv2.cvtColor(cnv_cut, cv2.COLOR_BGR2HSV)
    bgrLower = np.array([0,0,100])    # 抽出する色の下限(BGR)
    bgrUpper = np.array([180,45,255])    # 抽出する色の上限(BGR)
    img_mask = cv2.inRange(hsv, bgrLower, bgrUpper) # BGRからマスクを作成
    result = cv2.bitwise_and(cnv_cut, cnv_cut, mask=img_mask)
    whitePixels = np.count_nonzero(cv2.cvtColor(result, cv2.COLOR_BGR2GRAY))
    
    if whitePixels == pix_1 == pix_2 == pix_3 and vaild == True and cnt - cnt_pre > 5:
        sleep_mode = sleep_check(text_cut)
        if sleep_mode == True:
            return
        cnt_pre = cnt
        click = True
        pyautogui.rightClick()

    height = conv_img.shape[0]
    width = conv_img.shape[1]
    cv2.putText(conv_img,
            text='count : ' + str(cnt),
            org=(80, 100),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=4.0,
            color=(0, 255, 0),
            thickness=5,
            lineType=cv2.LINE_4)
    cv2.putText(conv_img,
            text='cnt_pre: ' + str(cnt_pre),
            org=(80, 250),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=4.0,
            color=(0, 255, 0),
            thickness=5,
            lineType=cv2.LINE_4)
    if first == False:
        cv2.putText(conv_img,
                text='fps : ' + str(format((1/(time_2 - time_1)),'.2f')),
                org=(80, 400),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=4.0,
                color=(0, 255, 0),
                thickness=5,
                lineType=cv2.LINE_4)
    cv2.putText(conv_img,
            text='whitepixel: ' + str(whitePixels),
            org=(80, 550),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=4.0,
            color=(0, 255, 0),
            thickness=5,
            lineType=cv2.LINE_4)
    cv2.putText(conv_img,
            text='pix_1: ' + str(pix_1),
            org=(80, 700),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=4.0,
            color=(0, 255, 0),
            thickness=5,
            lineType=cv2.LINE_4)
    cv2.putText(conv_img,
            text='pix_2: ' + str(pix_2),
            org=(80, 850),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=4.0,
            color=(0, 255, 0),
            thickness=5,
            lineType=cv2.LINE_4)
    cv2.putText(conv_img,
            text='pix_3: ' + str(pix_3),
            org=(80, 1000),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=4.0,
            color=(0, 255, 0),
            thickness=5,
            lineType=cv2.LINE_4)
    cv2.putText(conv_img,
            text='click: ' + str(click),
            org=(80, 1150),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=4.0,
            color=(0, 255, 0),
            thickness=5,
            lineType=cv2.LINE_4)
    cv2.putText(conv_img,
            text='vaild: ' + str(vaild),
            org=(80, 1300),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=4.0,
            color=(0, 255, 0),
            thickness=5,
            lineType=cv2.LINE_4)
    '''
    cv2.putText(conv_img,
            text='text: ' + str(text_in),
            org=(80, 1450),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=4.0,
            color=(0, 255, 0),
            thickness=5,
            lineType=cv2.LINE_4)
    '''
    conv_img = cv2.resize(conv_img,(int(width/2), int(height/2)))

    cv2.imshow('output', conv_img)
    cv2.imshow('cnv', result)
    #cv2.imshow('text',text_cut)
    
    pix_3 = pix_2
    pix_2 = pix_1
    pix_1 = whitePixels


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

    if first == True:
        time_1 = time.time()

    time_2 = time.time()   
    
    if sleep_mode == True and sleep_vaild == True:
        if bed_in_flg == False and mojinokori == False:
            bed_in()
            bed_in_flg = True
            pyautogui.rightClick()
            pyautogui.rightClick()
            time.sleep(1)
        elif wakeup_check(conv_img) == True:
            mojinokiori = True
            bed_out()
            bed_in_flg = False
            sleep_mode = False
    elif sleep_mode == False:
        mojinokori = False
        turi_mode(conv_img,time_1,time_2)

    time_1 = time_2
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