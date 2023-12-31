from json2tex.HomebrewRenderer import HomebrewRenderer
from json2tex.DocumentRenderer import DocumentRenderer

def renderExampleAdventure():
    adventureRenderer = HomebrewRenderer("./AnExampleAdventure.json")
    adventureRenderer.render() #Renders the example adventure and writes it to a .tex file
    adventureRenderer.convertToPdf() #converts the .tex file to a .pdf file and cleans up the working directory

def renderRenderingDemo():
    testRenderer = DocumentRenderer()
    testRenderer.setContentData("./renderDemo.json") #Download the 5e.tools renderdemo and safe it in this directory to run this
    testRenderer.setMeta("RenderDemo", "", "5e.tools")
    testRenderer.additionalHeaderOptions.append("\\onecolumn")
    testRenderer.render() #Renders the renderdemo
    testRenderer.convertToPdf()

renderExampleAdventure()
