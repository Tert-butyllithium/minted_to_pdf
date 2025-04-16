# Extract Minted Snippets


This repository contains a Python script and template for extracting and transforming `minted` code blocks from a LaTeX document into standalone PDF snippets. This approach enables you to keep the syntax highlighting from Pygments locally, while **removing** the `minted` environment from your main `.tex` files—making it suitable for arXiv submissions (which don’t allow `minted` + shell-escape).

## Contents

- **`extract_minted_linebased.py`**  
  A Python script that processes LaTeX files **line by line** to locate `\begin{minted}` blocks, extract their code, compile them into standalone PDFs, and replace them with `\includegraphics` references.  

- **`template_standalone.tex`**  
  A LaTeX template for the snippet PDF documents. It includes a `minted` environment with placeholders for the code and minted options (like `[linenos]{python}`).

- **`minted_snippets/`** (generated at runtime)  
  A folder created by the script to store the snippet `.tex` files and the compiled `.pdf` output.

## Features

1. **Line-based** detection of minted blocks, which can be more robust than a single multiline regex.  
2. **Customizable** ignoring of code lines starting with `@` (or any other filters you choose).  
3. **Standalone** snippet compilation, so the main LaTeX files end up with `\includegraphics` references only—no minted usage remains in the final `.tex` you’ll submit.

## Prerequisites

- **Python 3**  
- A working LaTeX environment (e.g. TeX Live, MikTeX) with the `minted` package installed locally.  
- The **pygmentize** tool (usually installed as part of Python’s Pygments or by system packages).  
  - This is required if `minted` is invoked during snippet compilation.  
- The script calls `pdflatex -shell-escape` by default. Adjust if you prefer `xelatex` or `lualatex`.

## Usage

1. **Prepare Your Template**  
   Make sure `template_standalone.tex` defines placeholders:
   ```latex
   \begin{minted}{{ minted_block_options }}
   {{ minted_code }}
   \end{minted}
    ```

    You can also add packages, color definitions, or custom minted styles here.

2.	Run the Script
    From your terminal, run:
    ```bash
    python extract_minted_linebased.py template_standalone.tex <file1.tex> [<file2.tex> ...]
    ```
    - `template_standalone.tex` is your snippet template.
	- `file1.tex`, `file2.tex`, etc. are the LaTeX files containing `\begin{minted}...\end{minted}` blocks.
  
3.	Output
	- For each input `<file>.tex`, the script produces a new `<file>_nominted.tex` which - no minted blocks—only `\includegraphics` references.
	- A folder named `minted_snippets/` is created (if it doesn’t already exist). Inside, you’ll find:
    	- `codeblock_1.tex/.pdf`, `codeblock_2.tex/.pdf`, etc. — one snippet for each minted block the script finds.

## Known Limitations
- **One-Line \begin{minted}**: The script expects each `\begin{minted}` plus its optional `[...]` and `{lang}` to appear on a single line. If you break them across multiple lines, the script won't detect them.
