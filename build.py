#!/bin/bash

# Install dependencies (Ubuntu): 
# sudo apt-get install pandoc texlive-latex-base texlive-fonts-recommended texlive-lang-spanish unoconv texlive-latex-extra
# sudo pip3 install pypdf2 

import re
import os
import tempfile
from subprocess import call
from PyPDF2 import PdfFileMerger, PdfFileReader

def generate_chapters_pdf(page_offset, book_style):
    chapters_directory = 'manuscrito'

    (_, monolitic_filepath) = tempfile.mkstemp()
    (_, chapters_pdf_filepath) = tempfile.mkstemp()
    chapters_pdf_filepath += '.pdf'

    pandoc_options = ["-V", "lang=es", "--from", "markdown+hard_line_breaks", "--toc", "--chapters"]
    if book_style:
        pandoc_options += ["-V", "documentclass=book"]
    else:
        pandoc_options += ["-V", "documentclass=report"]
    
    with open(monolitic_filepath, 'w') as monolitic_file:
        monolitic_file.write('\n\n\\setcounter{page}{%s}\n\n' % page_offset)
        for filepath in sorted(os.listdir(chapters_directory)):
            with open(os.path.join(chapters_directory, filepath), 'rU') as chapter_file:
                if filepath.startswith('c'):
                    copy_chapter_content(chapter_file, monolitic_file)

    call(["pandoc"] + pandoc_options + ["--output", chapters_pdf_filepath, monolitic_filepath])

    return chapters_pdf_filepath


def copy_chapter_content(chapter_file, dst_file):
    i = 0
    for line in chapter_file:
        if line == '## Navegación\n':
            break
        if i == 0:
            # Remove number from chapter header.
            line = re.sub(r'^# ([0-9]+)\.(.*)', r'# \2', line)

        line = re.sub(r'(?<!\w)-(?!-)', '--', line) # Replace dialog '-'s with '--'s
        
        dst_file.write(line)
        i += 1

def generate_readme_sections_pdf(book_style):
    section_headers = ['## Sinopsis', '## Licencia', '## Agradecimientos']

    (_, temp_filepath) = tempfile.mkstemp()
    (_, readme_sections_pdf_filepath) = tempfile.mkstemp()
    readme_sections_pdf_filepath += '.pdf'

    with open(temp_filepath, 'w') as temp_file:
        temp_file.write('\\pagenumbering{gobble}\n\n') # No page numbers.
        with open('README.md', 'rU') as readme_file:
            copy_line = False
            for line in readme_file:
                if line.startswith('#'):
                    temp_file.write('\\newpage')
                    if line[:-1] in section_headers:
                        if book_style:
                            temp_file.write('\\mbox{}\n\n\\thispagestyle{empty}\n\n\\newpage\n\n')
                        else:
                            temp_file.write('\\newpage\n\n')
                    copy_line = line[:-1] in section_headers

                if copy_line:
                    if line.startswith('#'):
                        temp_file.write(line[1:]) # Make header top level.
                    else:
                        temp_file.write(line)

        temp_file.write('\\mbox{}\n\n\\thispagestyle{empty}\n\n\\newpage\n\n')

    call(["pandoc"] + ["--from", "markdown-implicit_figures", "--output", readme_sections_pdf_filepath, temp_filepath])

    return readme_sections_pdf_filepath

def generate_end_note_pdf(page_offset):
    (_, temp_filepath) = tempfile.mkstemp()
    (_, end_note_pdf_filepath) = tempfile.mkstemp()
    end_note_pdf_filepath += '.pdf'

    with open(temp_filepath, 'w') as temp_file:
        with open('manuscrito/nota-final.md', 'rU') as src_file:
            temp_file.write('\n\n\\setcounter{page}{%s}\n\n' % page_offset)
            for line in src_file:
                if line == '## Navegación\n':
                    break
                temp_file.write(line)

    call(["pandoc"] + ["--output", end_note_pdf_filepath, temp_filepath])

    return end_note_pdf_filepath

def generate_cover_pdf():
    (_, cover_pdf_filepath) = tempfile.mkstemp()
    cover_pdf_filepath += '.pdf'

    call(["unoconv"] + ["--output", cover_pdf_filepath, 'portada.odt'])

    return cover_pdf_filepath

if __name__ == "__main__":
    configurations = [
        {
            'file_name': 'libro-cuarto-poder.pdf',
            'book_style': True
        },
        {
            'file_name': 'cuarto-poder.pdf',
            'book_style': False
        },
    ]

    for configuration in configurations:
        cover_pdf_filepath = generate_cover_pdf()
        readme_sections_pdf_filepath = \
            generate_readme_sections_pdf(book_style=configuration['book_style'])
        chapters_pdf_filepath = generate_chapters_pdf(page_offset=8, 
            book_style=configuration['book_style'])
        end_note_pdf_filepath = generate_end_note_pdf(page_offset=141)
            
        pdf_merger = PdfFileMerger()
        pdf_merger.append(PdfFileReader(open(cover_pdf_filepath, 'rb')))
        pdf_merger.append(PdfFileReader(open(readme_sections_pdf_filepath, 'rb')))
        pdf_merger.append(PdfFileReader(open(chapters_pdf_filepath, 'rb')))
        pdf_merger.append(PdfFileReader(open(end_note_pdf_filepath, 'rb')))
        pdf_merger.write(configuration['file_name'])
