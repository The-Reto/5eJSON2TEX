import json
import os
import warnings
import re

class TexRenderer:

    class StatBlockRenderer:
        def __init__(self):
            self.lines = []
        def renderInlineStatBlock(self, monsterData, doubleWidht = False):
            self.lines.append("\\begin{DndMonster}[width=\\textwidth @WIDTHMOD + 8pt]{@MONSTERNAME}".replace("@MONSTERNAME", monsterData.get("name")))
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

    class InTextTagRenderer:
        '''
        Resolves all tags in a string
        '''
        @staticmethod
        def renderLine(line):
            TagPattern = "\{@.*?\}"
            tags = re.findall(TagPattern, line)
            while tags:
                for tag in tags:
                    line = TexRenderer.InTextTagRenderer.renderTag(line, tag)
                tags = re.findall(TagPattern, line)
            return line

        '''
        resolves a single tag in a string
        '''
        @staticmethod
        def renderTag(line, tag):
            if re.findall("{@b .*?}", tag) or re.findall("{@bold .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderTextFormatTag(line, tag, "\\textbf{", "{@bold ", "{@b ")
            elif re.findall("{@i .*?}", tag) or re.findall("{@italic .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderTextFormatTag(line, tag, "\\textit{", "{@italic ", "{@i ")
            elif re.findall("{@u .*?}", tag) or re.findall("{@underline .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderTextFormatTag(line, tag, "\\underline{", "{@underline ", "{@u ")
            elif re.findall("{@s .*?}", tag) or re.findall("{@strike .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderTextFormatTag(line, tag, "\\sout{", "{@strike ", "{@s ")
            elif re.findall("{@highlight .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderTextFormatTag(line, tag, "\\hl{", "{@highlight ")
            elif re.findall("{@sub .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderTextFormatTag(line, tag, "\\textsubscript{", "{@sub ")
            elif re.findall("{@sup .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderTextFormatTag(line, tag, "\\textsuperscript{", "{@sup ")
            elif re.findall("{@code .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderTextFormatTag(line, tag, "\\texttt{", "{@code ")
            elif re.findall("{@dice .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderDiceTag(line, tag)
            elif re.findall("{@damage .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderDiceTag(line.replace("{@damage ", "{@dice "), tag.replace("{@damage ", "{@dice "))
            elif re.findall("{@hit .*?}", tag):
                return TexRenderer.InTextTagRenderer.removeTag(line, tag, "{@hit ", "+")
            elif re.findall("{@dc .*?}", tag):
                return TexRenderer.InTextTagRenderer.removeTag(line, tag, "{@dc ", "DC ")
            elif re.findall("{@h}", tag):
                return line.replace(tag, "\\textit{Hit:} ")
            elif re.findall("{@skill .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderReferenceTag(line ,tag, "{@skill ")
            elif re.findall("{@spell .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderReferenceTag(line ,tag, "{@spell ")
            elif re.findall("{@condition .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderReferenceTag(line ,tag, "{@condition ")
            elif re.findall("{@atk .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderAttackTag(line ,tag)
            elif re.findall("{@creature .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderReferenceTag(line ,tag, "{@creature ")
            elif re.findall("{@item .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderReferenceTag(line ,tag, "{@item ")
            elif re.findall("{@class .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderReferenceTag(line ,tag, "{@class ")
            elif re.findall("{@vehicle .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderReferenceTag(line ,tag, "{@vehicle ")
            elif re.findall("{@adventure .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderBookTag(line ,tag, "{@adventure ")
            elif re.findall("{@book .*?}", tag):
                return TexRenderer.InTextTagRenderer.renderBookTag(line ,tag, "{@book ")
            else:
                warnings.warn("\nThe following Tag has not yet been implemented: " + tag, category=RuntimeWarning)
                return line.replace(tag, "UNRESOLVED-TAG: (" + tag.replace("{","(").replace("}",")") + ")")

        @staticmethod
        def renderAttackTag(line, tag):
            if tag == "{@atk mw,rw}": tagStr = "\\textsl{Melee or Ranged Weapon Attack:}"
            if tag == "{@atk rw}": tagStr =  "\\textsl{Ranged Weapon Attack:}"
            if tag == "{@atk mw}": tagStr =  "\\textsl{Melee Weapon Attack:}"
            return line.replace(tag, tagStr)

        @staticmethod
        def removeTag(line, tag, tagName, replacementStart = "", replacementEnd = ""):
            return line.replace(tag, tag.replace(tagName, replacementStart).replace("}",replacementEnd))

        @staticmethod
        def renderBookTag(line, tag, type):
            if type == "{@adventure ":
                displayText = re.findall("( [A-z].*?\|)", tag)[0].replace("|", "")
                reference = tag.replace(re.findall("(.*?\|[A-z].*?\|[0-9]\|)", tag)[0], "").replace("}", "")
                reference = reference.replace(" ", "_")
                replacement = "\hyperref[sec:@REF]{\\dotuline{@TEXT}}".replace("@REF", reference).replace("@TEXT", displayText)
                return line.replace(tag, replacement)
            ""
            if type == "{@book ":
                displayText = re.findall("( [A-z].*?\|)", tag)[0].replace("|", "")
                reference = re.findall("(\|[A-z]+?\|)", tag)[0].replace("|", "")
                chapter = re.findall("(\|[0-9]+?\|)", tag)[0].replace("|", "")
                replacement = "@TEXT\\footnote{see: @REF chapter @CHAP}".replace("@TEXT", displayText).replace("@REF", reference).replace("@CHAP", chapter)
                return line.replace(tag, replacement)

        @staticmethod
        def renderReferenceTag(line, tag, type):
            if re.findall(type + ".*?\|.*?}", tag):
                if re.findall(type + ".*?\|\|.*?}", tag):
                    "Reference with display name, but no source"
                    displayName = tag.replace(re.findall("(^.*?\|\|)", tag)[0], "").replace("}", "")
                    actualName = re.findall("( [A-z].*?\|)", tag)[0].replace("|", "")
                    source = ""
                elif re.findall("(.*?\|[A-z].*?\|)", tag):
                    "Reference with display name and source"
                    displayName = tag.replace(re.findall("(.*?\|[A-z].*?\|)", tag)[0], "").replace("}", "")
                    actualName = re.findall("( [A-z].*?\|)", tag)[0].replace("|", "")
                    source = re.findall("(\|[A-z].*?\|)", tag)[0].replace("|", "")
                elif re.findall("(\|[A-z]*?})", tag):
                    "Reference with source"
                    displayName = tag.replace(re.findall("(\|[A-z]*?})", tag)[0], "").replace(type,"")
                    actualName = displayName.title()
                    source = re.findall("(\|[A-z]*?})", tag)[0].replace("|", "").replace("}", "")
                else: 
                    print("More complicated - SOMETHING IS WRONG")
                    displayName =  "TOO COMPLICATED REFERENCE TAG"
                    source = "COULDN'T FIND SOURCE"
                    actualName = "COULDN'T FIND ACTUAL NAME"
                actualName = actualName.title()
                return TexRenderer.InTextTagRenderer.renderReference(line, tag, displayName, source, actualName)
            else:
                return TexRenderer.InTextTagRenderer.renderTextFormatTag(line, tag, "\\textit{", type)

        @staticmethod
        def renderReference(line, tag, displayName, source="", actualName=""):
            creatureStr = "\\textit{" + displayName + "}"
            if not source == "" or not actualName == "":
                creatureStr += "\\footnote{use "
                if not actualName == "":
                    creatureStr += actualName
                else:    
                    creatureStr += displayName
                if not source == "":    
                    creatureStr += " from " + source
                creatureStr += "}"
            return line.replace(tag, creatureStr)

        @staticmethod
        def renderDiceTag(line, tag):
            if (re.findall("{@dice [0-9]+d[0-9]?.+}", tag)): return line.replace(tag, tag.replace("{@dice ", "\\DndDice{"))
            else: return line.replace(tag, tag.replace("{@dice ", "").replace("}", ""))

        @staticmethod
        def renderTextFormatTag(line, tag, formatStr, tagStart, tagShort = None):
            if tagShort: return line.replace(tag, tag.replace(tagStart, tagShort).replace(tagShort, formatStr))
            else: return line.replace(tag, tag.replace(tagStart, formatStr))
        
    def __init__(self):
        self.inAppendix = False
        self.f_name = "UnnamedFile"
        self.temp_name = "5eJSON2TEX_UnnamedFile"

    '''
    Main routine. Renders a 5e.tools compatible JSON into a PDF using LaTex
    Inputs:
        JSONPath: Path to JSON File, as a str
    '''
    def renderAdventure(self, JSONPath):
        lines = []
        with open(JSONPath) as file:
            self.jsonData = json.load(file)
        self.f_name = self.jsonData.get("adventure")[0].get("name").replace(" ", "_")
        if "storyline" in self.jsonData.get("adventure")[0]: self.f_name = self.jsonData.get("adventure")[0].get("storyline").replace(" ", "_") + "_" + self.f_name
        self.temp_name = "_".join(["5eJSON2TEX",self.f_name])
        lines += TexRenderer.setUpDocument(self.jsonData.get("_meta"), self.jsonData.get("adventure")[0])
        lines += self.renderContent(self.jsonData.get("adventureData")[0].get("data"))
        lines += TexRenderer.closeDocument()
        self.writeTex(lines)

    '''
    Writes the Latex header to the 'lines' container
    Inputs:
        metaData: '_meta' object from the JSON file, as a dict
        adventureData: 'adventure' object from the JSON file, as a dict
    '''
    def setUpDocument(metaData, adventureData):
        header = '''\\documentclass[10pt,twoside,twocolumn,openany,nodeprecatedcode]{dndbook}
\\usepackage[utf8]{inputenc}
\\usepackage{tabulary}
\\usepackage[normalem]{ulem}
\\usepackage{color,soul}
\\usepackage{float}
\\usepackage{caption}
\\usepackage{wrapfig}
\\usepackage[normalem]{ulem}
\\usepackage[colorlinks=true,linkcolor=black,anchorcolor=black,citecolor=black,filecolor=black,menucolor=black,runcolor=black,urlcolor=black]{hyperref}
\\title{@DOCUMENT_TITLE \\\\ \\large @DOCUMENT_SUBTITLE}
\\author{@AUTHORS}
\\DndSetThemeColor[PhbMauve]
\\begin{document}
\\maketitle
\\addcontentsline{toc}{chapter}{Table Of Contents}
\\tableofcontents
\\newpage'''
        header = header.replace("@DOCUMENT_TITLE", adventureData.get("name"))
        header = header.replace("@DOCUMENT_SUBTITLE", adventureData.get("storyline"))
        header = header.replace("@AUTHORS", " ".join(metaData.get("sources")[0].get("authors")))
        return [header]

    '''
    Appends the final lines to the 'lines' container for rendering
    '''
    def closeDocument():
        end = "\\end{document}"
        return [end]

    '''
    Writes the data in the 'lines' to a .tex file in order
    Input:
        adventureData: 'adventure' object from the JSON file, as a dict
    '''
    def writeTex(self, lines):
        subEnvLevel = 0
        passedChapterHeading = False
        inAppendix = False
        fs = re.compile(r"([^,.]+)")
        part = re.compile(r"^(.+)\s(.+)")
        wmod = re.compile(r"(@WIDTHMOD)")
        with open(self.temp_name+".tex", 'w') as f:
            for line in lines:
                finalLine = TexRenderer.InTextTagRenderer.renderLine(line) + "\n"
                if line == "@STARTSUBENVIRONMENT": 
                    finalLine = ""
                    subEnvLevel += 1
                if line == "@ENDSUBENVIRONMENT": 
                    finalLine = ""
                    subEnvLevel -= 1
                if re.findall(wmod, finalLine):
                    if (inAppendix): finalLine = finalLine.replace("@WIDTHMOD", "")
                    else: finalLine = finalLine.replace("@WIDTHMOD", " / 2 ")
                    print(finalLine)
                if passedChapterHeading and not finalLine.startswith("\\") and subEnvLevel == 0 and re.match(fs, finalLine):
                    fsentence = re.search(fs, finalLine).group(1)
                    if len(fsentence) > 35: replaceP = re.search(part, fsentence[0:35]).group(1)
                    else: replaceP = fsentence
                    new = "\\DndDropCapLine{" + replaceP.replace(replaceP[0], replaceP[0]+"}{", 1) + "}"
                    finalLine = finalLine.replace(replaceP, new,1)
                    passedChapterHeading = False
                if finalLine.startswith("\\chapter{"): 
                    if finalLine.startswith("\\chapter{Appendix}"): inAppendix = True
                    else: 
                        inAppendix = False
                        passedChapterHeading = True
                f.write(finalLine)

    '''
    Calls pdflatex to convert the generated tex file to a pdf and clean up the output
    '''
    def convertToPdf(self):
        print("Compiling PDF from tex... (this can take a couple of seconnds)")
        os.system("pdflatex "+self.temp_name+".tex")
        os.system("pdflatex "+self.temp_name+".tex >/dev/null 2>&1")
        print("Cleaning up output files...")
        os.system("mv "+self.temp_name+".tex "+self.f_name+".tex")
        os.system("mv "+self.temp_name+".pdf "+self.f_name+".pdf")
        os.system("rm "+self.temp_name+"*")
        os.system("rm -r JSON2TEX_img")
        print("Done!")

    '''
    Renders adventure content to the 'lines' container
    Inputs:
        content: data object of the adventureData field in the JSON, as a dict.
    '''
    def renderContent(self, content):
        lines = []
        for chapter in content:
            lines += self.renderRecursive(0, chapter)
        return lines

    '''
    Main rendering routine. Can be called recursively.
    Reads the 'type' field of the 'data' input and
    Inputs:
        depth: recursion depth (used to detirmine the type of header: from chapter down to subparagraph)
        data: general JSON object
    '''
    def renderRecursive(self, depth, data):
        lines = []
        if isinstance(data, str):
            lines += [data + "\n"]
        elif data.get("type") == "section" or data.get("type") == "entries":
            lines += self.renderSection(depth, data)
        elif data.get("type") == "inset":
            lines += self.renderInset(depth, data)
        elif data.get("type") == "insetReadaloud":
            lines += self.renderReadAloudInset(depth, data)
        elif data.get("type") == "table":
            lines += TexRenderer.renderTable(data)
        elif data.get("type") == "list":
            lines += TexRenderer.renderList(data)
        elif data.get("type") == "quote":
            lines += TexRenderer.renderQuote(data)
        elif data.get("type") == "image":
            lines += TexRenderer.renderImage(data)
        elif data.get("type") == "statblockInline":
            lines += self.renderStatblock(data)
        elif data.get("type") == "statblock":
            lines += self.renderStatblock(data)
        else:
            warnings.warn("\nThe following type of JSON-Entry has not yet been implemented: " + data.get("type") + "\nThe entry will be skipped!", category=RuntimeWarning)
        return lines

    '''
    Renders section and chapter headers, then proceedes to recursively loop through the data inside the 'entries' field, again calling renderRecursive with depth increased by 1.
    '''
    def renderSection(self, depth, data):
        titles = [
        "\\chapter{",
        "\\section{",
        "\\subsection{",
        "\\subsubsection{",
        "\\paragraph{",
        "\\subparagraph{"
        ]
        lines = []
        if "name" in data:
            if data.get("name") == "Appendix":
                lines += ["\\onecolumn"]
            lines += [str(titles[depth] + data.get("name") + "} \\label{sec:" + data.get("name").replace(" ", "_") + "}")]
        for section in data.get("entries"):
            lines += self.renderRecursive(depth+1, section)
        return lines

    '''
    Renders an inset. The content of the inset is passed through renderRecursive again.
    '''
    def renderInset(self, depth, data):
        lines = ["@STARTSUBENVIRONMENT"]
        name = ""
        if "name" in data: name = data.get("name")
        lines += ["\\begin{DndComment}{" + name + "}"]
        for section in data.get("entries"):
            lines += self.renderRecursive(depth+1, section)
        lines += ["\\end{DndComment}\n"]
        lines += ["@ENDSUBENVIRONMENT"]
        return lines

    '''
    Renders a read aloud inset. The content of the inset is passed through renderRecursive again.
    '''
    def renderReadAloudInset(self, depth, data):
        name = ""
        lines = ["@STARTSUBENVIRONMENT"]
        if "name" in data: name = data.get("name")
        lines += ["\\begin{DndReadAloud}{" + name + "}"]
        for section in data.get("entries"):
            lines += self.renderRecursive(depth+1, section)
        lines += ["\\end{DndReadAloud}\n"]
        lines += ["@ENDSUBENVIRONMENT"]
        return lines

    '''
    Renders tables. Currently column content is written directly to the lines container without going through the renderer again.
    '''
    def renderTable(data):
        lines = ["@STARTSUBENVIRONMENT"]
        titles = data.get("colLabels")
        alignments = data.get("colStyles")
        alignments = " ".join(alignments).replace("text-align-left", "X").replace("text-align-center", "c")
        if "caption" in data: lines += [str("\\begin{DndTable}[header=@CAPTION]{".replace("@CAPTION", data.get("caption")) + alignments + "}\n")]
        else: lines += ["\\begin{DndTable}{" + alignments + "}\n"]
        if (titles): lines += [str(" & ".join(titles) + "\\\\")]
        for row in data.get("rows"):
            lines += [" & ".join(row) + "\\\\"]
        lines += [str("\\end{DndTable}\n\n")]
        lines += ["@ENDSUBENVIRONMENT"]
        return lines

    '''
    Renders tables. Currently item content is written directly to the lines container without going through the renderer again.
    This means that 'item' objects will currently break this routine.
    Also list styles are currently ignored.
    '''
    def renderList(data):
        lines = ["@STARTSUBENVIRONMENT"]
        lines += ["\\begin{itemize}\n"]
        for item in data.get("items"):
            if (isinstance(item, str)): lines += ["\\item " + item]
        lines += ["\\end{itemize}\n\n"]
        lines += ["@ENDSUBENVIRONMENT"]
        return lines

    '''
    Renders the quote environment.
    '''
    def renderQuote(data):
        lines = ["@STARTSUBENVIRONMENT"]
        lines += ["\\begingroup\n\\DndSetThemeColor[DmgLavender]\\begin{DndSidebar}{}"]
        lines += ["\\Large \centering «"]
        for line in data.get("entries"):
            lines += ["\\large \centering " + line + ""]
        lines += ["\\Large »\n \n \\normalsize \\raggedleft \\textit{ - " + data.get("by") + ", " + data.get("from")+"}"]
        lines += ["\\end{DndSidebar}\n\\endgroup"]
        lines += ["@ENDSUBENVIRONMENT"]
        return lines

    '''
    Adds an image. Currently this will not work with remote images (ie. the standard in 5eJSONS - this is the only point where the standard 5eJSON syntax does not work).
    '''
    def renderImage(data):
        lines = ["@STARTSUBENVIRONMENT"]
        if data.get("href").get("type") == "external":
            try:
                import requests
                image_url = data.get("href").get("url")
                r = requests.get(image_url)
                os.system("mkdir ./JSON2TEX_img")
                file_name = "./JSON2TEX_img/" + str(hash(image_url))+".png"
                with open(file_name,'wb') as f:
                    f.write(r.content)
                lines += ["\\begingroup\n\\DndSetThemeColor[DmgLavender]\\begin{figure}[H]\n\\centering"]
                lines += ["\includegraphics[width = 0.8 \\textwidth]{" + file_name + "}"]
                if "title" in data or "credit" in data: 
                    caption = []
                    if "title" in data: caption.append(data.get("title"))
                    if "credit" in data: caption.append("\\textit{" + data.get("credit") + "}")
                    lines += ["\caption*{" + "\\\\ \\footnotesize Source: ".join(caption) + "}"]
                lines += ["\\end{figure}\n\\endgroup"]
            except:
                warnings.warn("\nSomething went wrong when rendering the image", category=RuntimeWarning)
        else: warnings.warn("\nImage rendering for 'internal' type not implemented", category=RuntimeWarning)
        lines += ["@ENDSUBENVIRONMENT"]
        return lines

    '''
    Renders statblocks
    '''
    def renderStatblock(self, data):
        renderer = TexRenderer.StatBlockRenderer()
        linesToAdd = ["@STARTSUBENVIRONMENT"]
        if data.get("type") == "statblockInline": linesToAdd += renderer.renderInlineStatBlock(data.get("data"))
        elif data.get("type") == "statblock":
            monsterData = self.jsonData.get("monster")
            monsterFound = False
            for monster in monsterData:
                if monster.get("name") == data.get("name"): 
                    linesToAdd += renderer.renderInlineStatBlock(monster)
                    monsterFound = True
            if not monsterFound: linesToAdd += ["Monster @MONSTERNAME not found in this source".replace("@MONSTERNAME", data.get("name"))]
        linesToAdd += ["@ENDSUBENVIRONMENT"]
        return linesToAdd