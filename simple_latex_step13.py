#!/usr/bin/env python3
"""
Simple LaTeX conversion for Step 13
Converts the paper with citations to LaTeX format without complex dependencies
"""

import json
import re
from pathlib import Path
from datetime import datetime

def clean_latex_text(text):
    """Clean and escape text for LaTeX"""
    # Replace special LaTeX characters
    replacements = {
        '%': '\\%',
        '$': '\\$',
        '&': '\\&',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}'
    }
    
    # Skip replacements in math mode
    math_pattern = r'\$[^$]+\$'
    math_blocks = re.findall(math_pattern, text)
    
    # Replace special chars outside math
    for char, replacement in replacements.items():
        # Temporarily replace math blocks
        temp_text = text
        for i, block in enumerate(math_blocks):
            temp_text = temp_text.replace(block, f"MATHBLOCK{i}")
        
        # Replace characters
        temp_text = temp_text.replace(char, replacement)
        
        # Restore math blocks
        for i, block in enumerate(math_blocks):
            temp_text = temp_text.replace(f"MATHBLOCK{i}", block)
        
        text = temp_text
    
    return text

def convert_markdown_to_latex(content):
    """Convert markdown content to LaTeX"""
    lines = content.split('\n')
    latex_lines = []
    in_code_block = False
    in_list = False
    
    for line in lines:
        # Handle code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                latex_lines.append('\\end{verbatim}')
                in_code_block = False
            else:
                latex_lines.append('\\begin{verbatim}')
                in_code_block = True
            continue
        
        if in_code_block:
            latex_lines.append(line)
            continue
        
        # Handle headers
        if line.startswith('# ') and not line.startswith('## '):
            # Title - skip as it's in the template
            continue
        elif line.startswith('## '):
            section_title = line[3:].strip()
            latex_lines.append(f'\\section{{{section_title}}}')
        elif line.startswith('### '):
            subsection_title = line[4:].strip()
            latex_lines.append(f'\\subsection{{{subsection_title}}}')
        
        # Handle lists
        elif line.strip().startswith('• ') or line.strip().startswith('- '):
            if not in_list:
                latex_lines.append('\\begin{itemize}')
                in_list = True
            item_text = line.strip()[2:]
            latex_lines.append(f'\\item {clean_latex_text(item_text)}')
        elif in_list and line.strip() == '':
            latex_lines.append('\\end{itemize}')
            in_list = False
            latex_lines.append('')
        
        # Handle citations
        elif '[CITE_' in line:
            # Replace citation placeholders
            line = re.sub(r'\[CITE_([^\]]+)\]', r'\\cite{\1}', line)
            latex_lines.append(clean_latex_text(line))
        
        # Handle bold and italic
        elif '**' in line or '*' in line:
            # Bold
            line = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', line)
            # Italic
            line = re.sub(r'\*([^*]+)\*', r'\\textit{\1}', line)
            latex_lines.append(clean_latex_text(line))
        
        # Handle equations (basic)
        elif line.strip().startswith('$') and line.strip().endswith('$'):
            latex_lines.append(line)  # Keep as-is for display math
        
        # Regular paragraphs
        else:
            if line.strip():
                latex_lines.append(clean_latex_text(line))
            else:
                latex_lines.append('')
    
    # Close any open list
    if in_list:
        latex_lines.append('\\end{itemize}')
    
    return '\n'.join(latex_lines)

def generate_bibliography(references):
    """Generate bibliography entries"""
    bib_entries = []
    
    # Define some common references
    default_refs = {
        "RELU": {
            "authors": "Vinod Nair and Geoffrey E. Hinton",
            "title": "Rectified Linear Units Improve Restricted Boltzmann Machines",
            "year": "2010",
            "venue": "ICML"
        },
        "GELU": {
            "authors": "Dan Hendrycks and Kevin Gimpel",
            "title": "Gaussian Error Linear Units (GELUs)",
            "year": "2016",
            "venue": "arXiv preprint arXiv:1606.08415"
        },
        "SWISH": {
            "authors": "Prajit Ramachandran and Barret Zoph and Quoc V. Le",
            "title": "Searching for Activation Functions",
            "year": "2017",
            "venue": "arXiv preprint arXiv:1710.05941"
        },
        "PRELU": {
            "authors": "Kaiming He and Xiangyu Zhang and Shaoqing Ren and Jian Sun",
            "title": "Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification",
            "year": "2015",
            "venue": "ICCV"
        }
    }
    
    # Generate bibliography
    for key, ref in default_refs.items():
        entry = f"\\bibitem{{{key}}}\n"
        entry += f"{ref['authors']}.\n"
        entry += f"\\newblock {{{ref['title']}}}.\n"
        entry += f"\\newblock In \\emph{{{ref['venue']}}}, {ref['year']}.\n"
        bib_entries.append(entry)
    
    return '\n\n'.join(bib_entries)

def create_latex_document(paper_content, image_files):
    """Create complete LaTeX document"""
    
    # Extract title and abstract
    title_match = re.search(r'^#\s+(.+)$', paper_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "AutoGELU Paper"
    
    abstract_match = re.search(r'## Abstract\s*\n\n(.+?)(?=\n##)', paper_content, re.DOTALL)
    abstract = abstract_match.group(1).strip() if abstract_match else ""
    
    # Convert main content
    main_content = convert_markdown_to_latex(paper_content)
    
    # Generate bibliography
    bibliography = generate_bibliography([])
    
    # Create LaTeX document
    latex_doc = r"""\documentclass[10pt]{article}

% Required packages
\usepackage[preprint]{neurips_2023}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{url}
\usepackage{hyperref}
\usepackage{color}
\usepackage{algorithm}
\usepackage{algorithmic}

% Title and authors
\title{""" + clean_latex_text(title) + r"""}

\author{
  Generated by AIRAS\\
  \texttt{https://github.com/auto-res/airas}
}

\begin{document}

\maketitle

\begin{abstract}
""" + clean_latex_text(abstract) + r"""
\end{abstract}

""" + main_content + r"""

\section*{References}
\small
\begin{thebibliography}{99}
""" + bibliography + r"""
\end{thebibliography}

\end{document}"""
    
    return latex_doc

def main():
    print("=== Simple LaTeX Conversion (Step 13) ===")
    
    # Load paper content
    print("\nLoading paper content...")
    try:
        with open("paper_with_citations.md", "r") as f:
            paper_content = f.read()
        print(f"Loaded paper content ({len(paper_content)} characters)")
    except FileNotFoundError:
        print("Error: paper_with_citations.md not found")
        return
    
    # Find image files
    image_files = []
    experiments_dir = Path("src/experiments")
    if experiments_dir.exists():
        image_files = list(experiments_dir.glob("*.pdf"))
        print(f"Found {len(image_files)} PDF images")
    
    # Convert to LaTeX
    print("\nConverting to LaTeX...")
    latex_content = create_latex_document(paper_content, image_files)
    
    # Create output directory
    output_dir = Path("latex_output")
    output_dir.mkdir(exist_ok=True)
    
    # Save LaTeX file
    latex_file = output_dir / "paper.tex"
    with open(latex_file, "w") as f:
        f.write(latex_content)
    print(f"Saved LaTeX document to: {latex_file}")
    
    # Create a simple neurips style file if needed
    style_content = r"""% neurips_2023.sty
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{neurips_2023}[2023/01/01 NeurIPS 2023 style]

\RequirePackage{times}
\RequirePackage[margin=1in]{geometry}

\newcommand{\preprint}{}

\endinput
"""
    
    style_file = output_dir / "neurips_2023.sty"
    with open(style_file, "w") as f:
        f.write(style_content)
    print(f"Created style file: {style_file}")
    
    # Copy images if they exist
    if image_files:
        print("\nCopying image files...")
        for img in image_files:
            dest = output_dir / img.name
            import shutil
            shutil.copy2(img, dest)
            print(f"Copied: {img.name}")
    
    # Create compilation script
    compile_script = output_dir / "compile.sh"
    with open(compile_script, "w") as f:
        f.write("""#!/bin/bash
# Compile LaTeX document
pdflatex paper.tex
pdflatex paper.tex  # Run twice for references
echo "PDF compilation complete!"
""")
    compile_script.chmod(0o755)
    
    # Save summary
    summary = {
        "step": "13_latex_conversion",
        "timestamp": datetime.now().isoformat(),
        "latex_file": str(latex_file),
        "image_files": [str(f.name) for f in image_files],
        "output_directory": str(output_dir),
        "compilation_command": "cd latex_output && pdflatex paper.tex"
    }
    
    with open("step13_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n=== LaTeX Conversion Complete ===")
    print(f"LaTeX files saved to: {output_dir}/")
    print("\nTo compile the PDF:")
    print(f"  cd {output_dir}")
    print("  pdflatex paper.tex")
    print("  pdflatex paper.tex  # Run twice for references")
    print("\nOr run the compile script:")
    print(f"  cd {output_dir} && ./compile.sh")

if __name__ == "__main__":
    main()