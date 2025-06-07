# Jupytercor Pandoc Filters

This directory contains Pandoc filters used by `jupytercor` to customize the conversion process.

## Filter Descriptions

-   **`pandoc-ldotcarreaux.py`**
    -   **Type**: Pandoc filter (Python 2/3, uses `pandocfilters`)
    -   **Target Format**: LaTeX
    -   **Purpose**: Converts empty code blocks into a LaTeX `\ldotcarreaux[$length]` command, where `$length` is the number of lines in the original empty code block. This is likely used for specific formatting in custom LaTeX templates like "cornouaille".
    -   **Used by**: `jupytercor.cli.convert_to_latex` and `jupytercor.cli.convert_to_pdf` when the "cornouaille" template is active.

-   **`pandoc-minted.py`**
    -   **Type**: Pandoc filter (Python 2/3, uses `pandocfilters`)
    -   **Target Format**: LaTeX
    -   **Purpose**: Transforms Pandoc `CodeBlock` elements into `minted` environments (e.g., `\begin{minted}{language} ... \end{minted}`) and `Code` elements into `\mintinline{language}{...}` commands. This enables high-quality syntax highlighting in LaTeX output via the `minted` package.
    -   **Used by**: Potentially by LaTeX conversions if a template is set up to use `minted`. (Note: Current `jupytercor` CLI doesn't explicitly call this for the default templates, but it's available. The "cornouaille" template uses `listings` by default).

-   **`panflute-breakline.py`**
    -   **Type**: Panflute filter (Python 3)
    -   **Target Format**: Affects intermediate processing.
    -   **Purpose**: Inserts line breaks before and after image elements during Pandoc's internal conversions. This can help control spacing around images, particularly when converting from Markdown to HTML as an intermediate step before cleaning to GitHub Flavored Markdown (GFM).
    -   **Used by**: `jupytercor.utils.clean_markdown` during the Markdown -> HTML conversion step.

-   **`panflute-bullet.py`**
    -   **Type**: Panflute filter (Python 3)
    -   **Target Format**: Affects intermediate processing or specific output formats.
    -   **Purpose**: Modifies bullet list items by appending a newline character to the content of each item. This can influence the spacing or rendering of lists in the final output.
    -   **Used by**: Not explicitly called by default in the current `jupytercor` main workflows, but available. Could be part of specific custom conversion chains if added.

-   **`panflute-headers.py`**
    -   **Type**: Panflute filter (Python 3)
    -   **Target Format**: LaTeX
    -   **Purpose**: Converts standard Pandoc `Header` elements (e.g., `# Heading 1`, `## Heading 2`) into the corresponding LaTeX sectioning commands (e.g., `\section{Heading 1}`, `\subsection{Heading 2}`).
    -   **Used by**: `jupytercor.cli.convert_to_latex` and `jupytercor.cli.convert_to_pdf` when the "cornouaille" template (or other similar LaTeX templates) are used, as these templates rely on LaTeX sectioning.
