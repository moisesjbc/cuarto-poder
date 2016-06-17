#!/bin/bash

# Install dependencies (Ubuntu): 
# sudo apt-get install pandoc texlive-latex-base texlive-fonts-recommended texlive-lang-spanish
# sudo pip3 install pypdf2

import re
import os
import tempfile
from subprocess import call

def generate_chapters_pdf(chapters_pdf_path):
    chapters_directory = 'manuscrito'

    (_, monolitic_filepath) = tempfile.mkstemp()

    with open(monolitic_filepath, 'w') as monolitic_file:
        for filepath in sorted(os.listdir(chapters_directory)):
            with open(os.path.join(chapters_directory, filepath), 'rU') as chapter_file:
                copy_chapter_content(chapter_file, monolitic_file)

    call(["pandoc"] + ["-V", "lang=es", "--toc", "--chapters", "--output", chapters_pdf_path, monolitic_filepath])

    return monolitic_filepath


def copy_chapter_content(chapter_file, dst_file):
    i = 0
    for line in chapter_file:
        if line == '## Navegación\n':
            break
        if i == 0:
            # Remove number from chapter header.
            line = re.sub(r'^# ([0-9]+)\.(.*)', r'# \2', line)
        dst_file.write(line)
        i += 1

def generate_readme_sections_pdf(dst_file):
    section_headers = ['## Sinopsis', '## Licencia', '## Agradecimientos']

    (_, temp_filepath) = tempfile.mkstemp()

    with open(temp_filepath, 'w') as temp_file:
        temp_file.write('\\pagenumbering{gobble}\n\n') # No page numbers.
        with open('README.md', 'rU') as readme_file:
            copy_line = False
            for line in readme_file:
                if line.startswith('#'):
                    temp_file.write('\\newpage')
                    copy_line = line[:-1] in section_headers

                if copy_line:
                    if line.startswith('#'):
                        temp_file.write(line[1:]) # Make header top level.
                    else:
                        temp_file.write(line)

    call(["pandoc"] + ["--output", dst_file, temp_filepath])

if __name__ == "__main__":
    generate_readme_sections_pdf('primeras-secciones.pdf')
    generate_chapters_pdf('capítulos.pdf')

    from PyPDF2 import PdfFileMerger, PdfFileReader
    pdf_merger = PdfFileMerger()
    pdf_merger.append(PdfFileReader(open('portada.pdf', 'rb')))
    pdf_merger.append(PdfFileReader(open('primeras-secciones.pdf', 'rb')))
    pdf_merger.append(PdfFileReader(open('capítulos.pdf', 'rb')))
    pdf_merger.write("cuarto-poder.pdf")
