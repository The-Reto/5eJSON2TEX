import json
import os
import warnings
import re

class TexRenderer:

    class StatBlockRenderer:
        def __init__(self):
            self.lines = []

        def renderInlineStatBlock(self, monsterData, doubleWidht = False):
            if doubleWidht: self.lines.append("\\begin{DndMonster}[width=\\textwidth + 8pt]{@MONSTERNAME}\n\\begin{multicols}{2}".replace("@MONSTERNAME", monsterData.get("name")))
            else: self.lines.append("\\begin{DndMonster}[width=\\textwidth / 2 + 8pt]{@MONSTERNAME}\n\\begin{multicols}{2}".replace("@MONSTERNAME", monsterData.get("name")))
            self.renderMonsterType(monsterData)
            self.renderMonsterBasics(monsterData)
            self.renderAbilityScores(monsterData)
            self.renderMonsterDetails(monsterData)
            self.renderMonsterActions(monsterData)
            self.lines.append("\\end{multicols}\n\\end{DndMonster}")
            return self.lines

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
        def renderLine(self, line):
            TagPattern = "\{@.*?\}"
            tags = re.findall(TagPattern, line)
            while tags:
                for tag in tags:
                    line = self.renderTag(line, tag)
                tags = re.findall(TagPattern, line)
            return line

        '''
        resolves a single tag in a string
        '''
        def renderTag(self, line, tag):
            if re.findall("{@b .*?}", tag) or re.findall("{@bold .*?}", tag):
                return self.renderTextFormatTag(line, tag, "\\textbf{", "{@bold ", "{@b ")
            elif re.findall("{@i .*?}", tag) or re.findall("{@italic .*?}", tag):
                return self.renderTextFormatTag(line, tag, "\\textit{", "{@italic ", "{@i ")
            elif re.findall("{@u .*?}", tag) or re.findall("{@underline .*?}", tag):
                return self.renderTextFormatTag(line, tag, "\\underline{", "{@underline ", "{@u ")
            elif re.findall("{@s .*?}", tag) or re.findall("{@strike .*?}", tag):
                return self.renderTextFormatTag(line, tag, "\\sout{", "{@strike ", "{@s ")
            elif re.findall("{@highlight .*?}", tag):
                return self.renderTextFormatTag(line, tag, "\\hl{", "{@highlight ")
            elif re.findall("{@sub .*?}", tag):
                return self.renderTextFormatTag(line, tag, "\\textsubscript{", "{@sub ")
            elif re.findall("{@sup .*?}", tag):
                return self.renderTextFormatTag(line, tag, "\\textsuperscript{", "{@sup ")
            elif re.findall("{@code .*?}", tag):
                return self.renderTextFormatTag(line, tag, "\\texttt{", "{@code ")
            elif re.findall("{@dice .*?}", tag):
                return self.renderDiceTag(line, tag)
            elif re.findall("{@damage .*?}", tag):
                return self.renderDiceTag(line.replace("{@damage ", "{@dice "), tag.replace("{@damage ", "{@dice "))
            elif re.findall("{@hit .*?}", tag):
                return self.removeTag(line, tag, "{@hit ", "+")
            elif re.findall("{@dc .*?}", tag):
                return self.removeTag(line, tag, "{@dc ", "DC ")
            elif re.findall("{@h}", tag):
                return line.replace(tag, "\\textit{Hit:} ")
            elif re.findall("{@skill .*?}", tag):
                return self.renderReferenceTag(line ,tag, "{@skill ")
            elif re.findall("{@spell .*?}", tag):
                return self.renderReferenceTag(line ,tag, "{@spell ")
            elif re.findall("{@condition .*?}", tag):
                return self.renderReferenceTag(line ,tag, "{@condition ")
            elif re.findall("{@atk .*?}", tag):
                return self.renderAttackTag(line ,tag)
            elif re.findall("{@creature .*?}", tag):
                return self.renderReferenceTag(line ,tag, "{@creature ")
            elif re.findall("{@item .*?}", tag):
                return self.renderReferenceTag(line ,tag, "{@item ")
            elif re.findall("{@class .*?}", tag):
                return self.renderReferenceTag(line ,tag, "{@class ")
            elif re.findall("{@vehicle .*?}", tag):
                return self.renderReferenceTag(line ,tag, "{@vehicle ")
            else:
                warnings.warn("\nThe following Tag has not yet been implemented: " + tag, category=RuntimeWarning)
                return line.replace(tag, "UNRESOLVED-TAG: (" + tag.replace("{","(").replace("}",")") + ")")

        def renderAttackTag(self, line, tag):
            if tag == "{@atk mw,rw}": tagStr = "\\textsl{Melee or Ranged Weapon Attack:}"
            if tag == "{@atk rw}": tagStr =  "\\textsl{Ranged Weapon Attack:}"
            if tag == "{@atk mw}": tagStr =  "\\textsl{Melee Weapon Attack:}"
            return line.replace(tag, tagStr)

        def removeTag(self, line, tag, tagName, replacementStart = "", replacementEnd = ""):
            return line.replace(tag, tag.replace(tagName, replacementStart).replace("}",replacementEnd))

        def renderReferenceTag(self, line, tag, type):
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
                return self.renderReference(line, tag, displayName, source, actualName.title())
            else:
                return self.renderTextFormatTag(line, tag, "\\textit{", type)

        def renderReference(self, line, tag, displayName, source="", actualName=""):
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

        def renderDiceTag(self, line, tag):
            if (re.findall("{@dice [0-9]+d[0-9]?.+}", tag)): return line.replace(tag, tag.replace("{@dice ", "\\DndDice{"))
            else: return line.replace(tag, tag.replace("{@dice ", "").replace("}", ""))

        def renderTextFormatTag(self, line, tag, formatStr, tagStart, tagShort = None):
            if tagShort: return line.replace(tag, tag.replace(tagStart, tagShort).replace(tagShort, formatStr))
            else: return line.replace(tag, tag.replace(tagStart, formatStr))
        
    def __init__(self):
        self.lines = []
        self.hadChapterHeading = False
        self.isString = False
        self.inSubEnvironment = False
        self.inAppendix = False
        self.f_name = "UnnamedFile"
        self.temp_name = "5eJSON2TEX_UnnamedFile"

    '''
    Main routine. Renders a 5e.tools compatible JSON into a PDF using LaTex
    Inputs:
        JSONPath: Path to JSON File, as a str
    '''
    def renderAdventure(self, JSONPath):
        with open(JSONPath) as file:
            self.jsonData = json.load(file)
        self.setUpDocument(self.jsonData.get("_meta"), self.jsonData.get("adventure")[0])
        self.renderContent(self.jsonData.get("adventureData")[0].get("data"))
        self.closeDocument()
        self.writeTex(self.jsonData.get("adventure")[0])

    '''
    Writes the Latex header to the 'lines' container
    Inputs:
        metaData: '_meta' object from the JSON file, as a dict
        adventureData: 'adventure' object from the JSON file, as a dict
    '''
    def setUpDocument(self, metaData, adventureData):
        header = '''\\documentclass[10pt,twoside,twocolumn,openany,nodeprecatedcode]{dndbook}
\\usepackage[utf8]{inputenc}
\\usepackage{tabulary}
\\usepackage[normalem]{ulem}
\\usepackage{color,soul}
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
        self.lines.append(header)

    '''
    Appends the final lines to the 'lines' container for rendering
    '''
    def closeDocument(self):
        end = "\\end{document}"
        self.lines.append(end)

    '''
    Writes the data in the 'lines' to a .tex file in order
    Input:
        adventureData: 'adventure' object from the JSON file, as a dict
    '''
    def writeTex(self, adventureData):
        self.f_name = "_".join([adventureData.get("storyline").replace(" ", "_"), adventureData.get("name").replace(" ", "_")])
        self.temp_name = "_".join(["5eJSON2TEX",self.f_name])
        with open(self.temp_name+".tex", 'w') as f:
            f.write('\n'.join(self.lines))

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
        os.system("rm "+self.temp_name+".*")
        print("Done!")

    '''
    Renders adventure content to the 'lines' container
    Inputs:
        content: data object of the adventureData field in the JSON, as a dict.
    '''
    def renderContent(self, content):
        for chapter in content:
            self.renderRecursive(0, chapter)

    '''
    Main rendering routine. Can be called recursively.
    Reads the 'type' field of the 'data' input and
    Inputs:
        depth: recursion depth (used to detirmine the type of header: from chapter down to subparagraph)
        data: general JSON object
    '''
    def renderRecursive(self, depth, data):
        if isinstance(data, str):
            self.renderString(data)
        elif data.get("type") == "section" or data.get("type") == "entries":
            self.renderSection(depth, data)
        elif data.get("type") == "inset":
            self.renderInset(depth, data)
        elif data.get("type") == "insetReadaloud":
            self.renderReadAloudInset(depth, data)
        elif data.get("type") == "table":
            self.renderTable(data)
        elif data.get("type") == "list":
            self.renderList(data)
        elif data.get("type") == "quote":
            self.renderQuote(data)
        elif data.get("type") == "image":
            self.renderImage(data)
        elif data.get("type") == "statblockInline":
            self.renderStatblock(data)
        elif data.get("type") == "statblock":
            self.renderStatblock(data)
        else:
            warnings.warn("\nThe following type of JSON-Entry has not yet been implemented: " + data.get("type") + "\nThe entry will be skipped!", category=RuntimeWarning)

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
        triggerAppendix = False
        if "name" in data:
            if data.get("name") == "Appendix":
                self.inAppendix = True
                triggerAppendix = True
                self.lines.append("\\onecolumn")
            self.appendLine(str(titles[depth] + data.get("name") + "}\n"))
        for section in data.get("entries"):
            self.renderRecursive(depth+1, section)
        if self.inAppendix and triggerAppendix:
            self.inAppendix = False

    '''
    Renders an inset. The content of the inset is passed through renderRecursive again.
    '''
    def renderInset(self, depth, data):
        self.inSubEnvironment = True
        name = ""
        if "name" in data: name = data.get("name")
        self.appendLine("\\begin{DndComment}{" + name + "}")
        for section in data.get("entries"):
            self.renderRecursive(depth+1, section)
        self.appendLine("\\end{DndComment}\n")
        self.inSubEnvironment = False

    '''
    Renders a read aloud inset. The content of the inset is passed through renderRecursive again.
    '''
    def renderReadAloudInset(self, depth, data):
        self.inSubEnvironment = True
        name = ""
        if "name" in data: name = data.get("name")
        self.appendLine("\\begin{DndReadAloud}{" + name + "}")
        for section in data.get("entries"):
            self.renderRecursive(depth+1, section)
        self.appendLine("\\end{DndReadAloud}\n")
        self.inSubEnvironment = False

    '''
    Renders tables. Currently column content is written directly to the lines container without going through the renderer again.
    '''
    def renderTable(self, data):
        self.inSubEnvironment = True
        titles = data.get("colLabels")
        alignments = data.get("colStyles")
        alignments = " ".join(alignments).replace("text-align-left", "X").replace("text-align-center", "c")
        if "caption" in data: self.appendLine(str("\\begin{DndTable}[header=@CAPTION]{".replace("@CAPTION", data.get("caption")) + alignments + "}\n"))
        else: self.appendLine(str("\\begin{DndTable}{" + alignments + "}\n"))
        if (titles): self.appendLine(str(" & ".join(titles) + "\\\\"))
        for row in data.get("rows"):
            self.appendLine(" & ".join(row) + "\\\\")
        self.appendLine(str("\\end{DndTable}\n\n"))
        self.inSubEnvironment = False

    '''
    Renders tables. Currently item content is written directly to the lines container without going through the renderer again.
    This means that 'item' objects will currently break this routine.
    Also list styles are currently ignored.
    '''
    def renderList(self, data):
        self.inSubEnvironment = True
        self.appendLine(str("\\begin{itemize}\n"))
        for item in data.get("items"):
            if (isinstance(item, str)): self.appendLine("\\item " + item)
        self.appendLine(str("\\end{itemize}\n\n"))
        self.inSubEnvironment = False

    '''
    Renders the quote environment.
    '''
    def renderQuote(self, data):
        self.inSubEnvironment = True
        self.appendLine("\\begingroup\n\\DndSetThemeColor[DmgLavender]\\begin{DndSidebar}{}")
        self.appendLine("\\Large \centering «")
        for line in data.get("entries"):
            self.appendLine("\\large \centering " + line + "")
        self.appendLine("\\Large »\n \n \\normalsize \\raggedleft \\textit{ - " + data.get("by") + ", " + data.get("from")+"}")
        self.appendLine("\\end{DndSidebar}\n\\endgroup")
        self.inSubEnvironment = False

    '''
    Adds an image. Currently this will not work with remote images (ie. the standard in 5eJSONS - this is the only point where the standard 5eJSON syntax does not work).
    '''
    def renderImage(self, data):
        '''self.inSubEnvironment = True
        self.appendLine("\\begingroup\n\\DndSetThemeColor[DmgLavender]\\begin{figure}\n\\centering")
        self.appendLine("\includegraphics[totalheight=8cm]{" + data.get("href").get("url") + "}")
        self.appendLine("\\end{figure}\n\\endgroup")
        self.inSubEnvironment = False'''
        warnings.warn("\nImage rendering currently disabled", category=RuntimeWarning)

    '''
    Renders statblocks
    '''
    def renderStatblock(self, data):
        self.inSubEnvironment = True
        renderer = TexRenderer.StatBlockRenderer()
        if data.get("type") == "statblockInline": linesToAdd = renderer.renderInlineStatBlock(data.get("data"), self.inAppendix)
        elif data.get("type") == "statblock":
            monsterData = self.jsonData.get("monster")
            monsterFound = False
            for monster in monsterData:
                if monster.get("name") == data.get("name"): 
                    linesToAdd = renderer.renderInlineStatBlock(monster, self.inAppendix)
                    monsterFound = True
            if not monsterFound: linesToAdd = ["Monster @MONSTERNAME not found in this source".replace("@MONSTERNAME", data.get("name"))]
        for line in linesToAdd:
            self.appendLine(line)
        self.inSubEnvironment = False

    '''
    Adds a simple string to the 'lines' container
    '''
    def renderString(self, line):
        self.isString = True
        self.appendLine(line + "\n")
        self.isString = False

    '''
    Appends a line to the 'lines' container, deals with in text tags.
    '''
    def appendLine(self, line):
        tagRenderer = TexRenderer.InTextTagRenderer()
        line = tagRenderer.renderLine(line)
        if line.startswith("\\chapter{"):
            self.hadChapterHeading = True
        elif self.hadChapterHeading and self.isString and not self.inSubEnvironment:
            if not line.startswith("\\"):
                fs = re.compile(r"([^,.]+)")
                part = re.compile(r"^(.+)\s(.+)")
                fsentence = re.search(fs, line).group(1)
                if len(fsentence) > 35: replaceP = re.search(part, fsentence[0:35]).group(1)
                else: replaceP = fsentence
                new = "\\DndDropCapLine{" + replaceP.replace(replaceP[0], replaceP[0]+"}{", 1) + "}"
                line = line.replace(replaceP, new,1)
                self.hadChapterHeading = False
        self.lines.append(line)