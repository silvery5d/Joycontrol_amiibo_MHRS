from paddleocr import PaddleOCR,draw_ocr
from PIL import Image
Image.DEBUG = False
from Talisman import Talisman
import numpy as np
import cv2
import matplotlib.pyplot as plt
from shapely import geometry

def recOneFrame(image, chest = 0):
    #识别技能
    rec_offset = np.array([263,-11,263,-11])
    _intpoints = [
        geometry.Point(781 + rec_offset[0]*chest ,288 + rec_offset[1]*chest),
        geometry.Point(781 + rec_offset[0]*chest ,338 + rec_offset[1]*chest),
        geometry.Point(932 + rec_offset[0]*chest ,202 + rec_offset[1]*chest)
    ]
    skills = []
    ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log = False)
    to_crop_areas = np.array([
        #(924,190,988,215), #rare level
        #(770,275,900,380), #skills name
        (700,0,1280,720)
    ])
    level_area = np.array([791,311,796,316])
    level_deltax = np.array([16,0,16,0])
    level_deltay = np.array([0,51,0,51])

    result = []
    for box in to_crop_areas:
        todec = image.crop(box + rec_offset * chest)
        todec.save('./todec.png')
        miniresult = ocr.ocr(np.array(todec), cls=False)
        for line in miniresult:
            for matrix in line[0]:
                matrix[0]+=box[0]+rec_offset[0] * chest
                matrix[1]+=box[1]+rec_offset[1] * chest
            result.append(line)
    boxes = [line[0] for line in result]
    
    txts_ori = [line[1][0] for line in result]
    #print("ORI",txts_ori)
    
    txts = []
    for r in range(len(txts_ori)):
        containcount = 0
        line = geometry.LineString(boxes[r])
        polygon = geometry.Polygon(line)
        for p in _intpoints:
            #print("POINT",p)
            if polygon.contains(p):
                #print("CONTAIN")
                containcount += 1
        if containcount > 0:
            txts.append(txts_ori[r])
    #print(txts)
    
    #识别技能等级
    level_det = np.zeros((2,3))
    if len(txts) >= 2:
        if len(txts[0]) == 5 or len(txts[0]) == 6 and txts[0][0:4] == 'RARE':
            if txts[0][4] == 'T':
                _rank = 7
            else:
                _rank = int(txts[0][4:])
        else:
            print("无法获取稀有度")
            return -1
        if len(txts) >= 4:
            todel = []
            for g in range(len(txts)):
                for h in range(len(txts)):
                    if (txts[g] in txts[h]) and (g!=h):
                        todel.append(g)
            for t in reversed(todel):
                del txts[t]
        for i in range(len(txts)-1):
            _skillid = Talisman.getSkillID(txts[i+1])
            _skilllv = 0
            for j in range(len(level_det[0])):
                todec = image.crop(level_area + i * level_deltay + j * level_deltax + rec_offset * chest)
                _avc = np.average(todec)
                level_det[i][j] = _avc
                if _avc < 150:
                    break
                _skilllv += 1
            skills.append([_skillid, _skilllv])
    else:
        print("无法识别技能",txts)
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
    decimg = []
    for l in range(4):
        img = np.array(Image.open('./slots/dec' + str(l+1)+'.tiff'))
        img1 = img.astype(np.uint8)
        decimg.append(img1)
    for i in range(3):
        todec = np.array(image.crop(slot_area + i * slot_delta + rec_offset * chest))
        todec = cv2.cvtColor(todec,cv2.COLOR_BGR2GRAY)

        counts = []
        for sn in range(len(slotsimg)):
            #print(len(todec),len(todec[0]),len(decimg[sn+1]),len(decimg[sn+1][0]))
            #print(sn+1)
            #print(decimg[sn+1])
            if sn > 0:
                todec *= decimg[sn-1] #去除装上装饰珠的影响
            delta = todec - slotsimg[sn] #计算待检测孔图标和标准孔图标的差值的绝对值
            for i in range(len(todec)):
                for j in range(len(todec[0])):
                    if todec[i][j] < slotsimg[sn][i][j]:
                        delta[i][j] = slotsimg[sn][i][j] - todec[i][j]

            c = 0
            for row in delta:
                for point in row:
                    if point > 80:
                        c += 1
            counts.append(c)
        _slotlv = np.argmin(counts)
        if np.min(counts) < 150:
            slots.append(_slotlv)
        else:
            print("出错了")                        
    #print( _rank, slots, skills)
    
    t = Talisman(_rank, slots[0], slots[1], slots[2], skills[0][0], skills[0][1], skills[1][0], skills[1][1])
    print(t.show())
    return t
