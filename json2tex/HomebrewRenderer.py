from json2tex.DocumentRenderer import DocumentRenderer
import json
'''
Renderer for the standard 5e.tools homebrew format
'''
class HomebrewRenderer(DocumentRenderer):
    def __init__(self, JSONPath):
        super().__init__()
        with open(JSONPath) as file:
            self.jsonData = json.load(file)

        subtitle = ""
        if "storyline" in self.jsonData.get("adventure")[0]: 
            subtitle = self.jsonData.get("adventure")[0].get("storyline")
        self.setMeta(self.jsonData.get("adventure")[0].get("name"), subtitle, ", ".join(self.jsonData.get("_meta").get("sources")[0].get("authors")))
        
        self.additionalHeaderOptions.append("\\DndSetThemeColor[PhbMauve]")

        self.contentData = self.jsonData.get("adventureData")[0].get("data")
        self.hasContentData = True

        if "monster" in self.jsonData: 
            self.creatureData = self.jsonData.get("monster")
            self.hasCreatureData = True
