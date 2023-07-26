from JSON2TEX import TexRenderer

renderer = TexRenderer.AdventureRenderer("./AnExampleAdventure.json")

renderer.renderAdventure() #Renders the adventure and writes it to a .tex file

renderer.convertToPdf() #converts the .tex file to a .pdf file and cleans up the working directory