# 5eJSON2TEX
A Python tool converting 5e.tools compatible JSON files to LaTeX (and ultimately PDF) form.
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
### How to use
You can istall this module by running the following code in the base directory of the repository
```
$ pip install .
```
After installing, refer to demo.py for example usage. The class HomebrewRenderer is set up to handle homebrew of the format found at https://github.com/TheGiddyLimit/homebrew (with `meta`, `adventure`, `andventureData`, etc. fields), while the DocumentRenderer is a more general class which can be used to render other 5e.tools compatible JSON-files.

Some manual editing of the LaTeX-file migth be preferable for optimal PDF outcome, but in general the auto-generated LaTeX is quite good - I'm even surprised by it and I wrote the bloodly converter.
<details>
<summary>`demo.py` details</summary>
#### `demo.py` details
As is the `demo.py` will render the contents of `AnExampleAdventure.json` with the standard settings (see the `renderExampleAdventure()` method for usage details). By exchanging the path provided you should be able to render any of the homebrew JSONs at https://github.com/TheGiddyLimit/homebrew to a .tex / .pdf file.

`demo.py` also includes a method for rendering the 5e.tools render demo (found under https://5e.tools/renderdemo.html), in order to use it create a file called `renderDemo.json` in the base directory with the following structure:
```
{
    "data": [
        \\COPY the renderdemo JSON from the website in here
    ]
}
```
**Important Note:** rendering the render demo does not yet work and will yield LaTeX errors!
</details>
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
- Statblocks (creatures only)
- Images (`external` type only)

*: Cells (in tables) or items (in lists) may currently only consist of strings, more involved objects (such as the "item" object for lists), will not work.
### Goal
The end goal is to have a tool that can fully convert 5e.tools compatible JSONs to LaTeX and therefore, PDFs, but that's a long way off.
A good first step would be if the converter could correctly render the JSON used in the 5e.tools render demo (https://5e.tools/renderdemo.html).
#### Next steps
- More in-text tags
- Formatted lists
- more complicated tables (where cell entries may be more than strings)
- more complicated lists (where entries may be more than strings)