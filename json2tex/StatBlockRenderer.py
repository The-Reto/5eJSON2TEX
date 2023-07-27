'''
Used to render Statblocks
'''
class StatBlockRenderer:
    def __init__(self):
        self.lines = []
    
    def renderInlineStatBlock(self, monsterData):
        if "_copy" in monsterData: return ["Cannot yet render copied monsterdata"]
        self.lines.append("\\begin{DndMonster}[width=\\linewidth + 8pt]{@MONSTERNAME}".replace("@MONSTERNAME", monsterData.get("name")))
        self.renderMonsterType(monsterData)
        self.renderMonsterBasics(monsterData)
        self.renderAbilityScores(monsterData)
        self.renderMonsterDetails(monsterData)
        self.lines.append("\\begin{multicols}{2}")
        self.renderMonsterActions(monsterData)
        self.lines.append("\\end{multicols}")
        self.renderMonsterFluff(monsterData)
        self.lines.append("\n\\end{DndMonster}")
        return self.lines

    def renderMonsterFluff(self, monsterData):
        if "fluff" in monsterData:
            if "entries" in monsterData.get("fluff"): 
                self.lines.append("\\DndMonsterSection{Info}\n")
                self.lines.extend(monsterData.get("fluff").get("entries"))

    def renderMonsterType(self, monsterData):
        sizes = {"T": "Tiny", "S": "Small", "M": "Medium", "L": "Large", "H": "Huge", "G": "Gargantuan"}
        alignments = {"L": "Lawful", "C": "Chaotic", "N": "Neutral", "G": "Good", "E": "Evil", "T": "True neutral", "U": "Unaligned", "A": "Any alignment"}
        typeStrs = []
        if "size" in monsterData:
            for size in monsterData.get("size"):
                typeStrs.append(sizes.get(size))
        if isinstance(monsterData.get("type"), str): typeStrs.append(monsterData.get("type").capitalize() + ",")
        else:
            type = monsterData.get("type")
            typeStr = type.get("type").capitalize()
            if "tags" in type: typeStr += " (@TAGS)".replace("@TAGS", ", ".join(type.get("tags")))                    
            typeStrs.append(typeStr + ",")
        if "alignment" in monsterData and monsterData.get("alignment"):
            for alignment in monsterData.get("alignment"):
                typeStrs.append(alignments.get(alignment))
        else: typeStrs.append(alignments.get("U"))
        self.lines.append("\\DndMonsterType{@MONSTERTYPE}".replace("@MONSTERTYPE", " ".join(typeStrs)))

    def renderAbilityScores(self, monsterData):
        scores = "\\DndMonsterAbilityScores[str = @STR,dex = @DEX,con = @CON,int = @INT,wis = @WIS,cha = @CHA]"
        scores = scores.replace("@STR", str(monsterData.get("str")))
        scores = scores.replace("@DEX", str(monsterData.get("dex")))
        scores = scores.replace("@CON", str(monsterData.get("con")))
        scores = scores.replace("@INT", str(monsterData.get("int")))
        scores = scores.replace("@WIS", str(monsterData.get("wis")))
        scores = scores.replace("@CHA", str(monsterData.get("cha")))
        self.lines.append(scores)

    def renderMonsterBasics(self, monsterData):
        basicStr = "\\DndMonsterBasics[armor-class = {@AC}, hit-points  = {@HP}, speed = {@SPEED}]"
        hp = "{@dice @FORMULA}".replace("@FORMULA", monsterData.get("hp").get("formula"))
        basicStr = basicStr.replace("@HP", hp)
        speed = self.renderSpeed(monsterData.get("speed"))
        basicStr = basicStr.replace("@SPEED", speed)
        ac = self.renderAC(monsterData.get("ac"))
        basicStr = basicStr.replace("@AC", ac)
        self.lines.append(basicStr)

    def renderSpeed(self, speedData):
        speeds = []
        for type in speedData.keys():
            if isinstance(speedData.get(type), int):
                speeds.append("@TYPE @SPEED ft.".replace("@TYPE", type).replace("@SPEED", str(speedData.get(type))))
            else:
                speed = speedData.get(type)
                speeds.append("@TYPE @SPEED ft. @COND".replace("@TYPE", type).replace("@SPEED", str(speed.get("number"))).replace("@COND", speed.get("condition")))
        return ", ".join(speeds)

    def renderMonsterSpellcasting(self, monsterData):
        spellData = monsterData.get("spellcasting")
        for casting in spellData:
            self.lines.append("\\DndMonsterAction{@NAME}".replace("@NAME",casting.get("name")))
            if "headerEntries" in casting: self.lines.append("\n".join(casting.get("headerEntries")))
            self.lines.append("\\\\")
            if "spells" in casting: self.renderSpellClass(casting.get("spells"), "spells")
            if "constant" in casting: self.renderSpellCategory(casting.get("constant"), "Constant")
            if "will" in casting: self.renderSpellCategory(casting.get("will"), "At Will")
            if "daily" in casting: self.renderSpellClass(casting.get("daily"), "daily")
            if "rest" in casting: self.renderSpellClass(casting.get("rest"), "rest")
            if "weekly" in casting: self.renderSpellClass(casting.get("weekly"), "weekly")
            if "yearly" in casting: self.renderSpellClass(casting.get("yearly"), "yearly")
            self.lines.append("\n \n")

    def renderSpellLevels(self, spellData):
        lowLevels = {"0":"Cantrips: ","1":"1st level (@SLOTS slots): ","2":"2nd level (@SLOTS slots): ", "3":"3rd level (@SLOTS slots): "}
        higherLevels = "@LEVELth level (@SLOTS slots): "
        for level in spellData.keys():
            if level in lowLevels: title = lowLevels.get(level)
            else: title = higherLevels.replace("@LEVEL", level)
            title = title.replace("@SLOTS", str(spellData.get(level).get("slots")))
            self.renderSpellCategory(spellData.get(level).get("spells"), title)

    def renderSpellClass(self, spellData, type):
        perTypes = {"daily":"@AMOUNT / Day: ","rest":"@AMOUNT / Rest: ","weekly":"@AMOUNT / Week: ","yearly":"@AMOUNT / Year: "}
        if type in perTypes:
            for amount in spellData.keys():
                title = perTypes.get(type).replace("@AMOUNT", amount)
                if amount[-1] == "e": 
                    title = title.replace(amount, amount.replace("e", "")).replace(":", " (each):")
                self.renderSpellCategory(spellData.get(amount), title)
        else:
            self.renderSpellLevels(spellData)

    def renderSpellCategory(self, spellData, title):
        spellStrs = spellData
        self.lines.append(title + ": " + ", ".join(spellStrs) + "\\\\")

    def renderAC(self, acData):
        ACs = []
        for ac in acData:
            if isinstance(ac, int):
                ACs.append(str(ac))
            else:
                AC = str(ac.get("ac"))
                if "from" in ac:
                    AC += " ( " + ", ".join(ac.get("from")) + ")"
                if "condition" in ac:
                    AC += " @COND".replace("@COND", ac.get("condition"))
                ACs.append(AC)
        return ", ".join(ACs)

    def renderMonsterDetails(self, monsterData):
        detailsStr = "\\DndMonsterDetails["
        details = []
        if "save" in monsterData:
            details.append("saving-throws = {" + self.renderListedDetails(monsterData.get("save")) + "}")
        if "skill" in monsterData:
            details.append("skills = {" + self.renderListedDetails(monsterData.get("skill")) + "}")
        if "vulnerable" in monsterData:
            details.append("damage-vulnerabilities = {" + self.renderGroupedDetails(monsterData.get("vulnerable"), "vulnerable") + "}")
        if "resist" in monsterData:
            details.append("damage-resistances = {" + self.renderGroupedDetails(monsterData.get("resist"), "resist") + "}")
        if "immune" in monsterData:
            details.append("damage-immunities = {" + self.renderGroupedDetails(monsterData.get("immune"), "immune") + "}")
        if "conditionImmune" in monsterData:
            details.append("condition-immunities = {" + self.renderGroupedDetails(monsterData.get("conditionImmune"), "conditionImmune") + "}")
        if "senses" in monsterData:
            senses = monsterData.get("senses")
            senses.append("Passive Perception " + str(monsterData.get("passive")))
            sensesStr = ", ".join(senses).replace(", " + senses[-1], " and " + senses[-1])
            details.append("senses = {" + sensesStr + "}")
        if "languages" in monsterData:
            languages = monsterData.get("languages")
            languagesStr = ", ".join(languages).replace(", " + languages[-1], " and " + languages[-1])
            details.append("languages = {" + languagesStr + "}")
        if "cr" in monsterData:
            details.append("challenge = {" + monsterData.get("cr") + "}")
        detailsStr += ", ".join(details) + "]"
        self.lines.append(detailsStr)

    def renderGroupedDetails(self, detailData, detailName):
        vunerableStrings = []
        for vun in detailData:
            if isinstance(vun, str): vunerableStrings.append(vun)
            else:
                pre = ""
                post = ""
                if "preNote" in vun: pre = vun.get("preNote")
                if "note" in vun: post = vun.get("note")
                vunerableStrings.append( pre + " " + self.renderGroupedDetails(vun.get(detailName), detailName) + " " + post )
        returnStr = ", ".join(vunerableStrings)
        return returnStr.replace(", " + vunerableStrings[-1], " and " + vunerableStrings[-1])

    def renderListedDetails(self, detailData):
        skillStrs = []
        for skill in detailData:
            skillStrs.append("{@skill " + skill.capitalize() + "} " + detailData.get(skill))
        returnStr = ", ".join(skillStrs)
        return returnStr.replace(", " + skillStrs[-1], " and " + skillStrs[-1])

    def renderMonsterActions(self, monsterData):
        if "trait" in monsterData:
            self.renderActions(monsterData.get("trait"))
        if "spellcasting" in monsterData:
            self.renderMonsterSpellcasting(monsterData)
        if "action" in monsterData:
            self.lines.append("\\DndMonsterSection{@TITLE}".replace("@TITLE", "Actions"))
            if "actionHeader" in monsterData:
                for entry in monsterData.get("actionHeader"): self.lines.append(entry)
            self.renderActions(monsterData.get("action"))
        if "bonus" in monsterData:
            self.lines.append("\\DndMonsterSection{@TITLE}".replace("@TITLE", "Bonusactions"))
            if "bonusHeader" in monsterData:
                for entry in monsterData.get("bonusHeader"): self.lines.append(entry)
            self.renderActions(monsterData.get("bonus"))
        if "reaction" in monsterData:
            self.lines.append("\\DndMonsterSection{@TITLE}".replace("@TITLE", "Reactions"))
            if "reactionHeader" in monsterData:
                for entry in monsterData.get("reactionHeader"): self.lines.append(entry)
            self.renderActions(monsterData.get("reaction"))
        if "legendary" in monsterData:
            self.lines.append("\\DndMonsterSection{@TITLE}".replace("@TITLE", "Legendary Actions"))
            if "legendaryHeader" in monsterData:
                for entry in monsterData.get("legendaryHeader"): self.lines.append(entry)
            self.renderActions(monsterData.get("legendary"))
        if "mythic" in monsterData:
            self.lines.append("\\DndMonsterSection{@TITLE}".replace("@TITLE", "Mythic Actions"))
            if "mythicHeader" in monsterData:
                for entry in monsterData.get("mythicHeader"): self.lines.append(entry)
            self.renderActions(monsterData.get("mythic"))

    def renderActions(self, actions):
        for trait in actions:
            self.lines.append("\\DndMonsterAction{@TRAITNAME}".replace("@TRAITNAME", trait.get("name")))
            for entry in trait.get("entries"):
                self.lines.append(entry + "\n")