#!/bin/bash
# Compile LaTeX document
pdflatex paper.tex
pdflatex paper.tex  # Run twice for references
echo "PDF compilation complete!"
