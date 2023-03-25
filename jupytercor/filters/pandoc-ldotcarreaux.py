#!/usr/bin/env python
# coding: utf-8
""" A pandoc filter that convert blank lines in ldotcarreaux
Usage:
    pandoc --filter ./ldotcarreaux.py -o myfile.tex myfile.md
"""

""" Here is the explanation for the code above:
1. We import the pandocfilters library and the Template class from the string library.
2. We define the function is_empty_cell. It takes a list of strings and returns a Boolean value.
3. We define the function unpack_code. It takes a dictionary and a string as arguments.
4. We define the function unpack_metadata. It takes a dictionary as argument.
5. We define the function ldotcarreaux. It takes four arguments: key, value, format, and meta.
6. We define a template. It is a string with a placeholder $longueur. The value of the placeholder will be replaced by the value of the key longueur in the dictionary code.
7. We define the function ldotcarreaux. It takes four arguments: key, value, format, and meta.
8. We test if the output format is latex.
9. We test if the key is CodeBlock.
10. We unpack the metadata.
11. We unpack the code.
12. We test if the code is empty. If it is, we return a list with a RawBlock element. Otherwise, we return nothing. """


""" This is an example for calling this function: 
import ldotcarreaux
ldotcarreaux.ldotcarreaux("CodeBlock", ["", ["text"], []], "latex", None)

It should return:

[RawBlock('latex', '\\ldotcarreaux[0]')] """


from string import Template
from typing import Dict, List

from pandocfilters import RawBlock, toJSONFilter


def is_empty_cell(source: List[str]) -> bool:
    """Determine if a cell is empty or contains only blank lines."""
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
        "estvide": is_empty_cell(contents),
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

    # If the code is empty, return None.
    if not code["estvide"]:
        return

    return [Element(format, template.substitute(code))]


if __name__ == "__main__":
    toJSONFilter(ldotcarreaux)
