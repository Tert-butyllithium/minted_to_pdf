#!/usr/bin/env python3

import os
import subprocess
import sys
import re

TEX_COMPILER = "pdflatex"  # or "xelatex", "lualatex", ...
SNIPPET_DIR = "minted_snippets"

# Regex to detect the start line of a minted block:
# We'll assume the entire \begin{minted}... is on one line.
# Example lines:
#   \begin{minted}{python}
#   \begin{minted}[linenos]{c}
# We'll capture the entire bracket+brace as group(1) - e.g. [linenos]{c} or {python}
BEGIN_RE = re.compile(r'^\s*\\begin{minted}(\[[^\]]*\])?\{([^}]+)\}')

# Regex to detect the end line of minted block:
END_RE = re.compile(r'^\s*\\end{minted}')

def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_minted_linebased.py <template.tex> <file1.tex> [<file2.tex> ...]")
        sys.exit(1)

    template_path = sys.argv[1]
    tex_files = sys.argv[2:]

    # Read template into memory
    with open(template_path, 'r', encoding='utf-8') as tf:
        template_text = tf.read()

    # Ensure snippet output directory
    os.makedirs(SNIPPET_DIR, exist_ok=True)

    for texfile in tex_files:
        print(f"Processing {texfile} ...")
        # Process line by line
        new_lines = []
        snippet_count = 0
        in_minted = False

        # We'll store minted options (like [linenos]{python}) in minted_opts
        minted_opts = ""
        # We'll store the code lines in minted_code
        minted_code_lines = []

        with open(texfile, 'r', encoding='utf-8') as f:
            for line in f:
                if not in_minted:
                    # Check if this line starts a minted block
                    match = BEGIN_RE.match(line)
                    if match:
                        # We are entering minted mode
                        in_minted = True
                        # Build something like: "[linenos]{c}" or just "{python}"
                        bracket_part = match.group(1) if match.group(1) else ""
                        lang_part = match.group(2) if match.group(2) else ""
                        minted_opts = bracket_part + "{" + lang_part + "}"
                        
                        # minted_code_lines = []  # Start fresh
                        minted_code_lines.clear()
                    else:
                        # Normal line, just keep it
                        new_lines.append(line)
                else:
                    # We are currently inside a minted block
                    end_match = END_RE.match(line)
                    if end_match:
                        # We reached the end of the minted block
                        in_minted = False
                        snippet_count += 1
                        
                        # 1) Filter lines (ignore those starting with "@")
                        filtered_code = []
                        for codeline in minted_code_lines:
                            if codeline.lstrip().startswith("@"):
                                continue
                            filtered_code.append(codeline)
                        
                        # 2) Prepare snippet .tex content from template
                        minted_opts = minted_opts.replace("footnotesize", "small")
                        
                        
                        snippet_tex = template_text
                        snippet_tex = snippet_tex.replace("{{ minted_block_options }}", minted_opts)
                        snippet_tex = snippet_tex.replace("{{ minted_code }}", "".join(filtered_code))
                        
                        snippet_name = f"codeblock_{snippet_count}"
                        snippet_tex_path = os.path.join(SNIPPET_DIR, snippet_name + ".tex")
                        
                        # Write snippet file
                        with open(snippet_tex_path, 'w', encoding='utf-8') as snipf:
                            snipf.write(snippet_tex)
                        
                        # 3) Compile the snippet
                        try:
                            subprocess.run(
                                [TEX_COMPILER, "-shell-escape", snippet_name + ".tex"],
                                cwd=SNIPPET_DIR,
                                check=True
                            )
                        except subprocess.CalledProcessError:
                            print(f"[ERROR] Compilation failed for {snippet_tex_path}", file=sys.stderr)
                        
                        # 4) Insert replacement lines in main doc
                        replacement = (
                            f"\\begin{{center}}\n"
                            f"\\includegraphics[width=\\linewidth]{{{SNIPPET_DIR}/{snippet_name}.pdf}}\n"
                            f"\\end{{center}}\n"
                        )
                        new_lines.append(replacement + "\n")
                        
                        # Reset for next block
                        minted_opts = ""
                        minted_code_lines.clear()
                    else:
                        # It's inside minted block; accumulate code
                        minted_code_lines.append(line)

        # Write out the updated .tex file
        out_tex = texfile.replace(".tex", "_nominted.tex")
        with open(out_tex, 'w', encoding='utf-8') as outf:
            outf.write("".join(new_lines))

        print(f" -> Wrote updated file: {out_tex}")
    print("Done.")


if __name__ == "__main__":
    main()