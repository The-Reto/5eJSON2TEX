from JSON2TEX import TexRenderer

renderer = TexRenderer()
renderer.renderAdventure("./AnExampleAdventure.json")
renderer.convertToPdf()