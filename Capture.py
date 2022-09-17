from paddleocr import PaddleOCR,draw_ocr
from PIL import Image
from Talisman import Talisman
import numpy as np
import cv2
import matplotlib.pyplot as plt

def captureFrame():
    cap = cv2.VideoCapture(0)
    cap.set(3,1280)
    cap.set(4,720)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("WIDTH  ",width,"HEIGHT  ",height)
    fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    if not cap.isOpened():
        return -1
    else:
        ret, frame = cap.read()
        frame = cv2.resize(frame,(1280,720),interpolation=cv2.INTER_CUBIC)
        if ret==True:
            b,g,r = cv2.split(frame)
            frame = cv2.merge([r,g,b])
            plt.imshow(frame)
            plt.show()
            cap.release()
        return Image.fromarray(frame)

def recOneFrame():
    #识别技能
    skills = []
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')
    to_crop_areas = [
        (924,190,988,215), #rare level
        (766,276,937,301), #skill1 name
        (766,326,937,351), #skill2 name
    ]
    level_area = np.array([791,311,796,316])
    level_deltax = np.array([16,0,16,0])
    level_deltay = np.array([0,51,0,51])
    image = captureFrame()
    #image = Image.open('./PNG image 3.PNG')
    image.save('capture.png')
    result = []
    for box in to_crop_areas:
        todec = image.crop(box)
        miniresult = ocr.ocr(np.array(todec), cls=False)
        #print(miniresult)
        for line in miniresult:
            for matrix in line[0]:
                matrix[0]+=box[0]
                matrix[1]+=box[1]
            result.append(line)
    txts = [line[1][0] for line in result]
    
    level_det = np.zeros((2,3))
    if len(txts) >= 2:
        if len(txts[0]) == 5 or len(txts[0]) == 6 and txts[0][0:4] == 'RARE':
            _rank = int(txts[0][4:])
        else:
            print("无法获取稀有度")
            return -1
        for i in range(len(txts)-1):
            _skillid = Talisman.getSkillID(txts[i+1])
            _skilllv = 0
            for j in range(len(level_det[0])):
                todec = image.crop(level_area + i * level_deltay + j * level_deltax)
                _avc = np.average(todec)
                level_det[i,j] = _avc
                if _avc < 150:
                    break
                _skilllv += 1
            skills.append([_skillid, _skilllv])
    else:
        print("无法识别技能")
        return -1
    if len(skills) < 2:
        skills.append([-1,0])
            
    #识别孔
    slots = []
    slot_area = np.array([905,214,929,237])
    slot_delta = np.array([28,0,28,0])
    slotsimg = []
    for k in range(5):
        img = np.array(Image.open('./slots/slot'+str(k)+'.png'))
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        slotsimg.append(img)
    for i in range(3):
        todec = np.array(image.crop(slot_area + i * slot_delta))
        todec = cv2.cvtColor(todec,cv2.COLOR_BGR2GRAY)

        counts = []
        for slot in slotsimg:
            delta = todec - slot
            c = 0
            for row in delta:
                for point in row:
                    if point > 80 and point < 180:
                        c += 1
            counts.append(c)
        _slotlv = np.argmin(counts)
        if np.min(counts) < 10:
            slots.append(_slotlv)
        else:
            print("出错了")                        
    print( _rank, slots, skills)
    
    return Talisman(_rank, slots[0], slots[1], slots[2], skills[0][0], skills[0][1], skills[1][0], skills[1][1])
