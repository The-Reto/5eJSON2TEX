from JSON2TEX import TexRenderer

renderer = TexRenderer()

renderer.renderAdventure("./AnExampleAdventure.json") #Renders the adventure and writes it to a .tex file

renderer.convertToPdf() #converts the .tex file to a .pdf file and cleans up the working directory