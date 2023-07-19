# 5eJSON2TEX
A Python tool converting 5e. tools compatible JSON files to LaTeX (and ultimately PDF) form.
It's nowhere near done, but it's a rudimentary skeleton of what might one day be.
## Notes
Some nice-to-know things
### In this Repository
In this repository, you'll find:
- The Python converter to convert 5e.tools compatible JSON files to Latex
- a demo Python script using the converter on the example provided
- an example JSON file containing an example adventure (mostly consisting of "Lorem Ipsum" text, just to show the formatting)
- the LaTeX file generated from the example JSON
- the PDF generated from the auto-generated LaTeX file
- this README
### Dependencies
In order to convert the generated Latex file to PDF, you'll need to have both
- pdflatex
- the DND 5E Latex Template (https://github.com/rpgtex/DND-5e-LaTeX-Template)
- Obviously, all relevant Python dependencies
## The Project
### Why?
Because I was homebrewing my own adventure (not, yet, public) using the 5e.tools tools and thought it'd be cool to also have my adventure as a PDF.
### Current State
The converter can currently convert adventures, in so far as it can display:
- Chapter-, section-, subsection-headings, etc.
- Base text, including a limited number of in-text tags ({@b }, {@i }, {@dice }, {@skill })
- Text Insets and "Read Aloud" Text Insets 
- Tables (limited*)
- Lists (limited*)
*: Cells (in tables) or items (in lists) may currently only consist of strings, more involved objects (such as the "item" object for lists), will not work.
### Goal
The end goal is to have a tool that can fully convert 5e.tools compatible JSONs to LaTeX and therefore, PDFs, but that's a long way off.
A good first step would be if the converter could correctly render the JSON used in the 5e.tools render demo (https://5e.tools/renderdemo.html).
#### Next steps
- Stat-blocks
- More in-text tags
- Images
