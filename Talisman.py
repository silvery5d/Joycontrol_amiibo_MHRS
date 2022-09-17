# 用于评价护石分数
# 需要配合Skills.xlsx使用
class Talisman:

    def __init__(self, rank, slot1, slot2, slot3, skillid1, skilllv1, skillid2, skilllv2):
        self.rank = rank
        self.slots = [slot1, slot2, slot3]        
        self.skill1 = [skillid1, skilllv1]
        self.skill2 = [skillid2, skilllv2]
        
    def calcScore(self):
        score = 0
        import pandas as pd
        skillsrank = pd.read_excel('.\Skills.xlsx',sheet_name='SkillsRank')
        skillsrank.set_index(["ID"], inplace = True)
        skillscore1 = skillsrank.loc[self.skill1[0],'Score']
        score += skillscore1 * self.skill1[1]
        if self.skill2[0] > 0:
            skillscore2 = skillsrank.loc[self.skill2[0],'Score']
            score += skillscore2 * self.skill2[1]

        slotsrank = pd.read_excel('.\Skills.xlsx',sheet_name='SlotsRank')
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
        import pandas as pd
        skillsrank = pd.read_excel('.\Skills.xlsx',sheet_name='SkillsRank')
        skillsrank.set_index(["ID"], inplace = True)
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
        print(s)
    
    def slotAmounts(self):
        import numpy
        #n的四位分别代表4孔，3孔，2孔，1孔数
        n = numpy.array([0,0,0,0])
        if self.slots[0] > 0:
            n[4-self.slots[0]] += 1
            if self.slots[1] > 0:
                n[4-self.slots[1]] += 1
                if self.slots[2] > 0:
                    n[4-self.slots[2]] += 1
        return n
    
    def getSkillID(name):
        import pandas as pd
        skillsrank = pd.read_excel('.\Skills.xlsx',sheet_name='SkillsRank')
        skillsrank.set_index(["ID"], inplace = True)
        _result = skillsrank.loc[skillsrank['Name'] == name].index.values.tolist()
        #print(_result)
        if len(_result) == 1:
            return _result[0]
        else: 
            print(name,"没有完全匹配")
            _possible1 = skillsrank.loc[skillsrank.Name.str.contains(name)].index.values.tolist()
            #print(_possible1)
            if len(_possible1) == 1:
                return _possible1[0]
            elif len(_possible1) > 1:
                #包含查找有多个结果
                return 0
            else:
                #包含查找没有结果
                return 0

    def canSupply(effslots, extraskills):        #有效孔能否提供这些技能
        import pandas as pd
        import numpy as np
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
        #print("SLOTSLIST", slotslist)
        
        skillsrank = pd.read_excel('.\Skills.xlsx',sheet_name='SkillsRank')
        skillsrank.set_index(["ID"], inplace = True)
        spspace=[]
        for _s in [_skill1, _skill2]:
            sid = _s[0]
            slv = _s[1]
            spt = []
            if _s[0] > 0:
                for slot in ['Slot4', 'Slot3', 'Slot2', 'Slot1']:
                    spt.append(skillsrank.loc[sid,slot])
                spt = np.array(spt)
                print(skillsrank.loc[sid,'Name'],spt)
                t = []
                for j in slotslist:
                    t.append(np.sum(j*spt))
                spspace.append(t)
                #print("SKILL POSSIBLE SPACE",spspace)#把所有的孔形成一列，其中每个孔如果要用来出1技能或者2技能，能加几级
        
        needlv = np.array([_skill1[1], _skill2[1]])
        ch = []
        for i in range(2**len(slotslist)):
            bstr = format(i,"b").zfill(len(slotslist))
            bi = []
            for j in range(len(slotslist)):
                bi.append(int(bstr[j]))
            ch.append(bi)
        ch = np.array(ch)
        lvpspace = []
        for i in range(len(ch)):
            #print(ch[i] * spspace[0],(ch[len(ch)-1]-ch[i])*spspace[1])
            #print(np.sum(ch[i] * spspace[0]),np.sum((ch[len(ch)-1]-ch[i])*spspace[1]))
            getlv = []
            t = []
            for j in range(len(spspace)):
                l = np.sum(ch[i] * spspace[j])
                t.append(l)
            getlv.append(t)
            getlv = np.array(getlv)
            #getlv = np.array([np.sum(ch[i] * spspace[0]),np.sum((ch[len(ch)-1]-ch[i])*spspace[1])])
            lvpspace.append(np.all(getlv >= needlv))
        print(lvpspace)
        if np.any(lvpspace):
            print("可覆盖技能")
            return True
        else:
            print("孔不足覆盖技能")
            return False
        
    def cover(self, b):
        import numpy as np
        #对象B必须是个护石
        if not isinstance (b,Talisman):
            print("b不是护石")
            return False

        #护石A的4孔数大于等于护石B的4孔数，4+3孔数，4+3+2孔数等同理
        deltaslots = self.slotAmounts() - b.slotAmounts()
        #print(deltaslots)
        sum = 0
        for i in deltaslots:
            sum += i
            if sum < 0:
                print("孔位不能覆盖")
                return False
            
        #如果等效大于零，则只保留没有被等效的孔。 
        effslots = np.array([0,0,0,0])
        effslots += deltaslots
        for j in range(4):
            if effslots[3-j] < 0:
                effslots[2-j] += effslots[3-j]
                effslots[3-j] = 0
        print("孔位覆盖，多出4321有效孔数",effslots)                                                   
        #只要a比b缺的技能可以用a的孔出出来，也是cover的 
        extraskills = []
        for _skill in [b.skill1,b.skill2]:
            #print(_skill)
            if _skill[0] > 0:
                _id = _skill[0]
                _lv = _skill[1]
                if (self.skill1[0] != _id) and (self.skill2[0] != _id):
                    #print("b有a没有的技能")
                    extraskills.append([_id, _lv])
                if (self.skill1[0] == _id) and (self.skill1[1] < _lv):
                    #print("b的1技能大于a的1技能")
                    extraskills.append([_id, _lv - self.skill1[1]])
                if (self.skill2[0] == _id) and (self.skill2[1] < _lv):
                    #print("b的1技能大于a的2技能")
                    extraskills.append([_id, _lv - self.skill2[1]])
        print("需要覆盖技能：",extraskills)
        if len(extraskills) == 0:
            return True
        else:
            return Talisman.canSupply(effslots, extraskills)