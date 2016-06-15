#!/bin/bash

# Install dependencies (Ubuntu): sudo apt-get install pandoc texlive-latex-base texlive-fonts-recommended

import os
import tempfile
from subprocess import call

def build_monolitic_file():
    chapters_directory = 'manuscrito'

    (_, monolitic_filepath) = tempfile.mkstemp()

    with open(monolitic_filepath, 'w') as monolitic_file:
        for filepath in sorted(os.listdir(chapters_directory)):
            with open(os.path.join(chapters_directory, filepath), 'rU') as chapter_file:
                copy_chapter_content(chapter_file, monolitic_file)

    return monolitic_filepath


def copy_chapter_content(chapter_file, dst_file):
    for line in chapter_file:
        if line == '## Navegación\n':
            break
        dst_file.write(line)


if __name__ == "__main__":
    monolitic_markdown_filepath = build_monolitic_file()

    call(["pandoc"] + ["--chapters", "--output", 'cuarto-poder.pdf', monolitic_markdown_filepath])
