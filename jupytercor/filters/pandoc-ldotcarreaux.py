#!/usr/bin/env python
""" A pandoc filter that convert blank lines in ldotcarreaux
Usage:
    pandoc --filter ./ldotcarreaux.py -o myfile.tex myfile.md
"""

from string import Template
from typing import Dict, List
from pandocfilters import toJSONFilter, RawBlock, RawInline


def est_vide_cell(source: List[str]) -> bool:
    """Determine if a cell is empty or contains only blank lines.
    """
    for elem in source:
        if elem != "" and elem != "\n":
            return False
    return True


def unpack_code(value: Dict, language: str) -> Dict:
    """Unpack the body and language of a pandoc code element.

    Args:
        value       contents of pandoc object
        language    default language
    """

    # get the language and attributes from the pandoc object
    [[_, classes, attributes], contents] = value
    if len(classes) > 0:
        language = classes[0]
    attributes = ", ".join("=".join(x) for x in attributes)

    # split the contents into lines
    lines = contents.split("\n")

    return {
        "contents": contents,
        "language": language,
        "attributes": attributes,
        "lines": lines,
        "longueur": len(lines),
        "estvide": est_vide_cell(contents),
        "message": "truc",
    }


def unpack_metadata(meta: dict) -> dict:
    """Unpack the metadata to get pandoc-ldotcarreaux settings.

    Args:
        meta    document metadata
    """
    settings = meta.get("pandoc-ldotcarreaux", {})
    if settings.get("t", "") == "MetaMap":
        settings = settings["c"]

        # Get language.
        language = settings.get("language", {})
        if language.get("t", "") == "MetaInlines":
            language = language["c"][0]["c"]
        else:
            language = None

        return {"language": language}

    else:
        # Return default settings.
        return {"language": "text"}


def ldotcarreaux(key: str, value: str, format: str, meta: dict) -> list:
    """
    Add ldotcarreaux
    Args:
        key     type of pandoc object
        value   contents of pandoc object
        format  target output format
        meta    document metadata
    """
    if format != "latex":
        return

    # Determine what kind of code object this is.
    if key == "CodeBlock":
        template = Template("\\ldotcarreaux[$longueur]\n")
        Element = RawBlock
    else:
        return

    settings = unpack_metadata(meta)

    code = unpack_code(value, settings["language"])

    # If the code is empty, return the ldotcarreaux
    if not code["estvide"]:
        return

    return [Element(format, template.substitute(code))]


if __name__ == "__main__":
    toJSONFilter(ldotcarreaux)
