#  用于评价护石分数
# 需要配合Skills.xlsx使用
import numpy as np
import pandas as pd
import math
skillsrank = pd.read_excel('./Skills.xlsx',sheet_name='SkillsRank')
skillsrank.set_index(["ID"], inplace = True)

class Talisman:
    def __init__(self, rank, slot1, slot2, slot3, skillid1, skilllv1, skillid2, skilllv2):
        self.rank = rank
        self.slots = [slot1, slot2, slot3]        
        self.skill1 = [skillid1, skilllv1]
        self.skill2 = [skillid2, skilllv2]
        
    def createFromLine(str):
        _l = np.array(str[:-2].split(','))
        _l = _l.astype(int)
        if len(_l)>=8:
            t = Talisman(_l[0],_l[1],_l[2],_l[3],_l[4],_l[5],_l[6],_l[7])
            return t
        else:
            return -1
        
    def createFromShow(str):
        words = str.split()
        print(words)
        rare = int(words[0][4:])
        print("RARE = ",rare)
        skills = []
        for sn in range(len(words)-2):
            print("SKILL ",words[sn+1])
            skillname = words[sn+1][:-1]
            #print("SKILLNAME ",skillname)
            skillid = skillsrank.loc[skillsrank['Name'] == skillname].index.values[0]
            print("SKILLID ",skillid)
            skilllevel = int(words[sn+1][-1:])
            #print("SKILLLEVEL ", skilllevel)
            skills.append([skillid,skilllevel])
        print("SKILLS ",skills)
        if len(skills) == 1:
            skills.append([-1,0])
        slotstring = words[len(words)-1].ljust(4,'0')
        print(slotstring)
        slots = []
        for i in range(3):
            slots.append(int(slotstring[i+1:i+2]))
        print("SLOTS ",slots)
        t = Talisman(rare,slots[0],slots[1],slots[2],skills[0][0],skills[0][1],skills[1][0],skills[1][1])
        return t
        
    def calcScore(self):
        score = 0
        skillscore1 = skillsrank.loc[self.skill1[0],'Score']
        score += skillscore1 * self.skill1[1]
        if self.skill2[0] > 0:
            skillscore2 = skillsrank.loc[self.skill2[0],'Score']
            score += skillscore2 * self.skill2[1]
        slotsrank = pd.read_excel('./Skills.xlsx',sheet_name='SlotsRank')
        slotsrank.set_index(["Slot"], inplace = True)
        score += slotsrank.loc[self.slots[0],'Score']
        score += slotsrank.loc[self.slots[1],'Score']
        score += slotsrank.loc[self.slots[2],'Score']
        return score
    
    def __str__(self):
        s = ""
        s += str(self.rank) + ","
        s += str(self.slots[0]) + ","
        s += str(self.slots[1]) + ","
        s += str(self.slots[2]) + ","
        s += str(self.skill1[0]) + ","
        s += str(self.skill1[1]) + ","
        s += str(self.skill2[0]) + ","
        s += str(self.skill2[1]) + ","
        return s
    
    def show(self):
        s = "RARE"+str(self.rank)+" "
        skillname1 = skillsrank.loc[self.skill1[0],'Name']
        s += skillname1 + str(self.skill1[1]) + " "
        if self.skill2[0] > 0:
            skillname2 = skillsrank.loc[self.skill2[0],'Name']
            s += skillname2 + str(self.skill2[1]) + " "
        if self.slots[0] > 0:
            s += "S" + str(self.slots[0])
            if self.slots[1] > 0:
                s += str(self.slots[1])
                if self.slots[2] > 0:
                    s += str(self.slots[2])
        #print(s)
        return s
    
    def slotAmounts(self):
        #n的四位分别代表4孔，3孔，2孔，1孔数
        n = np.array([0,0,0,0])
        if self.slots[0] > 0:
            n[4-self.slots[0]] += 1
            if self.slots[1] > 0:
                n[4-self.slots[1]] += 1
                if self.slots[2] > 0:
                    n[4-self.slots[2]] += 1
        return n
    
    def getSkillID(name):
        _result = skillsrank.loc[skillsrank['Name'] == name].index.values.tolist()
        if len(_result) == 1:
            sid = _result[0]
            print("结果:", skillsrank.loc[sid,'Name'])
            return sid
        else: 
            l = len(name)
            _possible = []
            for x in range(l):#x为一共去掉几个字
                for y in range(x+1):#y为在左边去掉几个字
                    sub = name[y:y-x+l]
                    #print("SUB",sub)
                    __possible = skillsrank.loc[skillsrank.Name.str.contains(sub)].Name.values.tolist()
                    _possible += __possible
            _possible = list(set(_possible))
            _scores = []
            for p in _possible:
                contains = 0
                for i in range(len(name)):
                    f = p.find(name[i])
                    if f >= 0:
                        contains += 1
                score = contains / len(name)
                _scores.append(score)
            maxindex = np.argmax(_scores)
            result = skillsrank.loc[skillsrank['Name'] == _possible[maxindex]].index.values[0]
            return result
                                                    
    def canSupply(effslots, extraskills, debug = False):        #有效孔能否提供这些技能
        _skill1 = extraskills[0]
        _skill2 = [0,0]
        if len(extraskills) > 1:
            _skill2 = extraskills[1]

        effslots_n =np.sum(effslots)
        slotslist =[]
        for _ in range(effslots_n):
            for i in range(4):
                if effslots[i] > 0:
                    li = [0,0,0,0]
                    li[i] = 1
                    slotslist.append(li)
                    effslots -= li
                    break
        if debug == True:
            print("SLOTSLIST 可用slot展开", slotslist)
        
        spspace=[]
        for _s in [_skill1, _skill2]:
            sid = _s[0]
            slv = _s[1]
            spt = []
            if _s[0] > 0:
                for slot in ['Slot4', 'Slot3', 'Slot2', 'Slot1']:
                    spt.append(skillsrank.loc[sid,slot])
                spt = np.array(spt)
                if debug == True:
                    print('技能: ',skillsrank.loc[sid,'Name'],'4至1孔可出技能',spt)
                t = []
                for j in slotslist:
                    t.append(np.sum(j*spt))
                spspace.append(t)
        if debug == True:
            print("SKILL POSSIBLE SPACE 可用slot分别可提供等级",spspace)#把所有的孔形成一列，其中每个孔如果要用来出1技能或者2技能，能加几级。
            #数组长度一定为2，分别代表两个技能。
            #下层数组长度为孔数，每个值代表每个孔用来出这个技能能出几级。
            #spspace[0]代表slotslist中的每个孔用来出技能1，得到的等级
            #spspace[1]代表slotslist中的每个孔用来出技能2，得到的等级
        
        needlv = np.array([_skill1[1], _skill2[1]])
        if debug == True:
            print("两个技能分别需要等级：",needlv)
        ch = []
        for i in range(2**len(slotslist)):
            bstr = format(i,"b").zfill(len(slotslist))
            bi = []
            for j in range(len(slotslist)):
                bi.append(int(bstr[j]))
            ch.append(bi)
        ch = np.array(ch)
        #ch中的每个元素代表一种可能性。
        #每个值中的1代表这个孔用于出skill1，0代表这个孔用于出skill2
        #ch用二进制的方法构建
        lvpspace = []
        for i in range(len(ch)):
            #i代表第几种可能性
            if debug == True:
                print("第",str(i+1),"/",str(len(ch)),"种可能性：")
                print("1和0代表出1或者2技能: ",ch[i])
                #print("两个技能分别得到：",ch[i] * spspace[0],(ch[len(ch)-1]-ch[i])*spspace[1])
                #print("两个技能等级求和",np.sum(ch[i] * spspace[0]),np.sum((ch[len(ch)-1]-ch[i])*spspace[1]))
            getlv_skill1 = np.sum(ch[i] * spspace[0])
            getlv_skill2 = 0
            if len(spspace) > 1:
                getlv_skill2 = np.sum((ch[len(ch)-1]-ch[i])*spspace[1])
            getlv = np.array([getlv_skill1,getlv_skill2])
            #getlv = np.array([np.sum(ch[i] * spspace[0]),np.sum((ch[len(ch)-1]-ch[i])*spspace[1])])

            if debug == True:
                print("实际得到等级GETLV",getlv)
            lvpspace.append(np.all(getlv >= needlv))
        if debug == True:
            print('每种可能性是否满足等级需求: ',lvpspace)
        if np.any(lvpspace):
            if debug == True:
                print("可覆盖技能")
            return True
        else:
            if debug == True:
                print("孔不足覆盖技能")
            return False
        
    def cover(self, b, debug = False):
        #对象B必须是个护石
        if not isinstance (b,Talisman):
            if debug == True:
                print("b不是护石")
            return False

        #护石A的4孔数大于等于护石B的4孔数，4+3孔数，4+3+2孔数等同理
        deltaslots = self.slotAmounts() - b.slotAmounts()
        if debug == True:
            print("DELTASLOTS:", deltaslots)
        sum = 0
        for i in deltaslots:
            sum += i
            if sum < 0:
                if debug == True:
                    print("孔位不能覆盖")
                return False
            
        #如果等效大于零，则只保留没有被等效的孔。 
        effslots = np.array([0,0,0,0])
        effslots += deltaslots
        for j in range(4):
            if effslots[3-j] < 0:
                effslots[2-j] += effslots[3-j]
                effslots[3-j] = 0
        if debug == True:
            print("孔位覆盖，多出4321有效孔数",effslots)                                                   
        #只要a比b缺的技能可以用a的孔出出来，也是cover的 
        extraskills = []
        for _skill in [b.skill1,b.skill2]:
            #print(_skill)
            if _skill[0] > 0:
                _id = _skill[0]
                _lv = _skill[1]
                if (self.skill1[0] != _id) and (self.skill2[0] != _id):
                    if debug == True:
                        print("b有a没有的技能")
                    extraskills.append([_id, _lv])
                if (self.skill1[0] == _id) and (self.skill1[1] < _lv):
                    if debug == True:
                        print("b的1技能大于a的1技能")
                    extraskills.append([_id, _lv - self.skill1[1]])
                if (self.skill2[0] == _id) and (self.skill2[1] < _lv):
                    if debug == True:
                        print("b的2技能大于a的2技能")
                    extraskills.append([_id, _lv - self.skill2[1]])
        if debug == True:
            print("需要覆盖技能：",extraskills)
        if len(extraskills) == 0:
            return True
        else:
            return Talisman.canSupply(effslots, extraskills, debug)
