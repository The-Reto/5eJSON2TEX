import warnings
import re
'''
Used to render the in-text-tags
'''
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
                line = InTextTagRenderer.renderTag(line, tag)
            tags = re.findall(TagPattern, line)
        return line

    '''
    resolves a single tag in a string
    '''
    @staticmethod
    def renderTag(line, tag):
        if re.findall("{@b .*?}", tag) or re.findall("{@bold .*?}", tag):
            return InTextTagRenderer.renderTextFormatTag(line, tag, "\\textbf{", "{@bold ", "{@b ")
        elif re.findall("{@i .*?}", tag) or re.findall("{@italic .*?}", tag):
            return InTextTagRenderer.renderTextFormatTag(line, tag, "\\textit{", "{@italic ", "{@i ")
        elif re.findall("{@u .*?}", tag) or re.findall("{@underline .*?}", tag):
            return InTextTagRenderer.renderTextFormatTag(line, tag, "\\underline{", "{@underline ", "{@u ")
        elif re.findall("{@s .*?}", tag) or re.findall("{@strike .*?}", tag):
            return InTextTagRenderer.renderTextFormatTag(line, tag, "\\sout{", "{@strike ", "{@s ")
        elif re.findall("{@highlight .*?}", tag):
            return InTextTagRenderer.renderTextFormatTag(line, tag, "\\hl{", "{@highlight ")
        elif re.findall("{@sub .*?}", tag):
            return InTextTagRenderer.renderTextFormatTag(line, tag, "\\textsubscript{", "{@sub ")
        elif re.findall("{@sup .*?}", tag):
            return InTextTagRenderer.renderTextFormatTag(line, tag, "\\textsuperscript{", "{@sup ")
        elif re.findall("{@code .*?}", tag):
            return InTextTagRenderer.renderTextFormatTag(line, tag, "\\texttt{", "{@code ")
        elif re.findall("{@dice .*?}", tag):
            return InTextTagRenderer.renderDiceTag(line, tag)
        elif re.findall("{@damage .*?}", tag):
            return InTextTagRenderer.renderDiceTag(line.replace("{@damage ", "{@dice "), tag.replace("{@damage ", "{@dice "))
        elif re.findall("{@hit .*?}", tag):
            return InTextTagRenderer.removeTag(line, tag, "{@hit ", "+")
        elif re.findall("{@dc .*?}", tag):
            return InTextTagRenderer.removeTag(line, tag, "{@dc ", "DC ")
        elif re.findall("{@h}", tag):
            return line.replace(tag, "\\textit{Hit:} ")
        elif re.findall("{@skill .*?}", tag):
            return InTextTagRenderer.renderReferenceTag(line ,tag, "{@skill ")
        elif re.findall("{@spell .*?}", tag):
            return InTextTagRenderer.renderReferenceTag(line ,tag, "{@spell ")
        elif re.findall("{@condition .*?}", tag):
            return InTextTagRenderer.renderReferenceTag(line ,tag, "{@condition ")
        elif re.findall("{@atk .*?}", tag):
            return InTextTagRenderer.renderAttackTag(line ,tag)
        elif re.findall("{@creature .*?}", tag):
            return InTextTagRenderer.renderReferenceTag(line ,tag, "{@creature ")
        elif re.findall("{@item .*?}", tag):
            return InTextTagRenderer.renderReferenceTag(line ,tag, "{@item ")
        elif re.findall("{@class .*?}", tag):
            return InTextTagRenderer.renderReferenceTag(line ,tag, "{@class ")
        elif re.findall("{@vehicle .*?}", tag):
            return InTextTagRenderer.renderReferenceTag(line ,tag, "{@vehicle ")
        elif re.findall("{@adventure .*?}", tag):
            return InTextTagRenderer.renderBookTag(line ,tag, "{@adventure ")
        elif re.findall("{@book .*?}", tag):
            return InTextTagRenderer.renderBookTag(line ,tag, "{@book ")
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
            try:
                displayText = re.findall("( [A-z].*?\|)", tag)[0].replace("|", "")
                reference = re.findall("(\|[A-z]+?\|)", tag)[0].replace("|", "")
                chapter = re.findall("(\|[0-9]+?\|)", tag)[0].replace("|", "")
                replacement = "@TEXT\\footnote{see: @REF chapter @CHAP}".replace("@TEXT", displayText).replace("@REF", reference).replace("@CHAP", chapter)
            except:
                replacement = "(UNRENDERED TAG)"
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
            return InTextTagRenderer.renderReference(line, tag, displayName, source, actualName)
        else:
            return InTextTagRenderer.renderTextFormatTag(line, tag, "\\textit{", type)

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

