import json
import os
import warnings
import re

class TexRenderer:

    class StatBlockRenderer:
        def __init__(self):
            self.lines = []

        def renderInlineStatBlock(self, data):
            monsterData = data.get("data")
            self.lines.append("\\begin{DndMonster}[width=\\textwidth / 2 + 8pt]{@MONSTERNAME}\n\\begin{multicols}{2}".replace("@MONSTERNAME", monsterData.get("name")))
            self.renderMonsterType(monsterData)
            self.renderAbilityScores(monsterData)
            self.renderMonsterBasics(monsterData)
            self.renderMonsterDetails(monsterData)
            self.renderMonsterActions(monsterData)
            self.lines.append("\\end{multicols}\n\\end{DndMonster}")
            return self.lines
        
        def renderMonsterType(self, monsterData):
            sizes = {"T": "Tiny", "S": "Small", "M": "Medium", "L": "Large", "H": "Huge", "G": "Gargantuan"}
            alignmentS = {"L": "Lawful", "C": "Chaotic", "N": "Neutral", "G": "Good", "E": "Evil", "T": "True neutral", "U": "Unaligned"}
            typeStrs = []
            for size in monsterData.get("size"):
                typeStrs.append(sizes.get(size))
            typeStrs.append(monsterData.get("type").capitalize() + ",")
            for alignment in monsterData.get("alignment"):
                typeStrs.append(alignmentS.get(alignment))
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
            self.lines.append("\\DndMonsterSection{Spellcasting}")
            self.lines.append("Spellcasting is NOT CURRENTLY IMPLEMENTED\n")

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

    f_name = "UnnamedFile"
    temp_name = "5eJSON2TEX_UnnamedFile"
    titles = [
        "\\chapter{",
        "\\section{",
        "\\subsection{",
        "\\subsubsection{",
        "\\paragraph{",
        "\\subparagraph{"
    ]

    def __init__(self):
        self.lines = []
        self.hadChapterHeading = False
        self.isString = False
        self.inSubEnvironment = False
        self.inAppendix = False

    '''
    Main routine. Renders a 5e.tools compatible JSON into a PDF using LaTex
    Inputs: 
        JSONPath: Path to JSON File, as a str
    '''
    def renderAdventure(self, JSONPath):
        with open(JSONPath) as file:
            jsonData = json.load(file)
        self.setUpDocument(jsonData.get("_meta"), jsonData.get("adventure")[0])
        self.renderContent(jsonData.get("adventureData")[0].get("data"))
        self.closeDocument()
        self.writeTex(jsonData.get("adventure")[0])

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
        else:
            warnings.warn("\nThe following type of JSON-Entry has not yet been implemented: " + data.get("type") + "\nThe entry will be skipped!", category=RuntimeWarning)

    '''
    Renders section and chapter headers, then proceedes to recursively loop through the data inside the 'entries' field, again calling renderRecursive with depth increased by 1.
    '''
    def renderSection(self, depth, data):
        triggerAppendix = False
        if "name" in data: 
            if data.get("name") == "Appendix":
                self.inAppendix = True
                triggerAppendix = True
                self.lines.append("\\onecolumn")
            self.appendLine(str(self.titles[depth] + data.get("name") + "}\n"))
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
        self.appendLine(str("\\begin{DndTable}{" + alignments + "}\n"))
        if (titles): self.appendLine(str(" & ".join(titles) + "\\\\"))
        for row in data.get("rows"):
            self.appendLine(str(" & ".join(row) + "\\\\"))
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
        for line in data.get("entries"):
            self.appendLine(line)
        self.appendLine("\n\\textit{" + data.get("by") + ", " + data.get("from")+"}")
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
        

    def renderStatblock(self, data):
        self.inSubEnvironment = True
        renderer = TexRenderer.StatBlockRenderer()
        linesToAdd = renderer.renderInlineStatBlock(data)
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
        TagPattern = "\{@.*?\}"
        tags = re.findall(TagPattern, line)
        while tags:
            for tag in tags:
                line = self.resolveTag(line, tag)
            tags = re.findall(TagPattern, line)
        else:
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

    '''
    Resolves in text tags this is ugly
    '''
    def resolveTag(self, line, tag):
        if re.findall("{@b .*?}", tag) or re.findall("{@bold .*?}", tag):
            return line.replace(tag, tag.replace("{@bold ", "{@b ").replace("{@b ", "\\textbf{"))
        elif re.findall("{@i .*?}", tag) or re.findall("{@italic .*?}", tag):
            return line.replace(tag, tag.replace("{@italic ", "{@i ").replace("{@i ", "\\textit{"))
        elif re.findall("{@u .*?}", tag) or re.findall("{@underline .*?}", tag):
            return line.replace(tag, tag.replace("{@underline ", "{@u ").replace("{@u ", "\\underline{"))
        elif re.findall("{@s .*?}", tag) or re.findall("{@strike .*?}", tag):
            return line.replace(tag, tag.replace("{@strike ", "{@s ").replace("{@s ", "\\sout{"))
        elif re.findall("{@highlight .*?}", tag):
            return line.replace(tag, tag.replace("{@highlight ", "\\hl{"))
        elif re.findall("{@sub .*?}", tag):
            return line.replace(tag, tag.replace("{@sub ", "\\textsubscript{"))
        elif re.findall("{@sup .*?}", tag):
            return line.replace(tag, tag.replace("{@sup ", "\\textsuperscript{"))
        elif re.findall("{@code .*?}", tag):
            return line.replace(tag, tag.replace("{@code ", "\\texttt{"))
        elif re.findall("{@dice .*?}", tag):
            return line.replace(tag, tag.replace("{@dice ", "\\DndDice{"))
        elif re.findall("{@damage .*?}", tag):
            return line.replace(tag, tag.replace("{@damage ", "\\DndDice{"))
        elif re.findall("{@hit .*?}", tag):
            return line.replace(tag, tag.replace("{@hit ", "+").replace("}",""))
        elif re.findall("{@skill .*?}", tag):
            return line.replace(tag, tag.replace("{@skill ", "\\textit{"))
        elif re.findall("{@atk .*?}", tag):
            return line.replace(tag, tag.replace("{@atk mw,rw}", "\\textsl{Melee or Ranged Weapon Attack:}").replace("{@atk mw}", "\\textsl{Melee Weapon Attack:}").replace("{@atk rw}", "\\textsl{Ranged Weapon Attack:}"))
        else:
            warnings.warn("\nThe following Tag has not yet been implemented: " + tag, category=RuntimeWarning)
            return line.replace(tag, "UNRESOLVED-TAG: (" + tag.replace("{","(").replace("}",")") + ")")
