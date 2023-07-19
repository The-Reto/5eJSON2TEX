import json
import os
import warnings
import re

class TexRenderer:
    lines = []
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
        self.convertToPdf()

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
        else:
            warnings.warn("\nThe following type of JSON-Entry has not yet been implemented: " + data.get("type") + "\nThe entry will be skipped!", category=RuntimeWarning)

    '''
    Renders section and chapter headers, then proceedes to recursively loop through the data inside the 'entries' field, again calling renderRecursive with depth increased by 1.
    '''
    def renderSection(self, depth, data):
        print(data.get("name"))
        if (isinstance(data.get("name"), str)): self.appendLine(str(self.titles[depth] + data.get("name") + "}\n"))
        for section in data.get("entries"):
            print(section)
            print(data.get("entries"))
            self.renderRecursive(depth+1, section)

    '''
    Renders an inset. The content of the inset is passed through renderRecursive again.
    '''
    def renderInset(self, depth, data):
        name = "" 
        if "name" in data: name = data.get("name")
        self.appendLine("\\begin{DndComment}{" + name + "}")
        for section in data.get("entries"):
            self.renderRecursive(depth+1, section)
        self.appendLine("\\end{DndComment}\n")
    
    '''
    Renders a read aloud inset. The content of the inset is passed through renderRecursive again.
    '''
    def renderReadAloudInset(self, depth, data):
        name = "" 
        if "name" in data: name = data.get("name")
        self.appendLine("\\begin{DndReadAloud}{" + name + "}")
        for section in data.get("entries"):
            self.renderRecursive(depth+1, section)
        self.appendLine("\\end{DndReadAloud}\n")

    '''
    Renders tables. Currently column content is written directly to the lines container without going through the renderer again.
    '''
    def renderTable(self, data):
        titles = data.get("colLabels")
        alignments = data.get("colStyles")
        alignments = " ".join(alignments).replace("text-align-left", "X").replace("text-align-center", "c")
        self.appendLine(str("\\begin{DndTable}{" + alignments + "}\n"))
        self.appendLine(str(" & ".join(titles) + "\\\\"))
        for row in data.get("rows"):
            self.appendLine(str(" & ".join(row) + "\\\\"))
        self.appendLine(str("\\end{DndTable}\n\n"))

    '''
    Renders tables. Currently item content is written directly to the lines container without going through the renderer again.
    This means that 'item' objects will currently break this routine.
    Also list styles are currently ignored.
    '''
    def renderList(self, data):
        self.appendLine(str("\\begin{itemize}\n"))
        for item in data.get("items"):
            if (isinstance(item, str)): self.appendLine("\\item " + item)
        self.appendLine(str("\\end{itemize}\n\n"))

    '''
    Renders the quote environment.
    '''
    def renderQuote(self, data):
        self.appendLine("\\begingroup\n\\DndSetThemeColor[DmgLavender]\\begin{DndSidebar}{}")
        for line in data.get("entries"):
            self.appendLine(line)
        self.appendLine("\n\\textit{" + data.get("by") + ", " + data.get("from")+"}")
        self.appendLine("\\end{DndSidebar}\n\\endgroup")

    '''
    Adds an image. Currently this will not work with remote images (ie. the standard in 5eJSONS - this is the only point where the standard 5eJSON syntax does not work).
    '''
    def renderImage(self, data):
        '''self.appendLine("\\begingroup\n\\DndSetThemeColor[DmgLavender]\\begin{figure}\n\\centering")
        self.appendLine("\includegraphics[totalheight=8cm]{" + data.get("href").get("url") + "}")
        self.appendLine("\\end{figure}\n\\endgroup")'''
        warnings.warn("\nImage rendering currently disabled", category=RuntimeWarning)

    '''
    Adds a simple string to the 'lines' container
    '''
    def renderString(self, line):
        self.appendLine(line + "\n")

    '''
    Appends a line to the 'lines' container, deals with in text tags. Recursive to deal with nested tags
    '''
    def appendLine(self, line):
        TagPattern = "\{@.*?\}"
        tags = re.findall(TagPattern, line)
        if tags:
            for tag in tags:
                line = self.resolveTag(line, tag)
            self.appendLine(line)
        else:
            self.lines.append(line)

    '''
    Resolves in text tags
    '''
    def resolveTag(self, line, tag):
        if re.findall("{@b .*?}", tag):
            return line.replace(tag, tag.replace("{@b ", "\\textbf{"))
        elif re.findall("{@i .*?}", tag):
            return line.replace(tag, tag.replace("{@i ", "\\textit{"))
        elif re.findall("{@dice .*?}", tag):
            return line.replace(tag, tag.replace("{@dice ", "").replace("}", ""))
        elif re.findall("{@skill .*?}", tag):
            return line.replace(tag, tag.replace("{@skill ", "\\textit{"))
        else:
            warnings.warn("\nThe following Tag has not yet been implemented: " + tag, category=RuntimeWarning)
            return line.replace(tag, "UNRESOLVED-TAG")


renderer = TexRenderer()
'''renderer.renderAdventure("./Heal_and_Deal_at_Ghir_Karnim.json")'''
renderer.renderAdventure("./AnExampleAdventure.json")
