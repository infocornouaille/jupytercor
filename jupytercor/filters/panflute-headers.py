from panflute import *

sectionTypes = ["section", "subsection", "subsubsection", "paragraph", "subparagraph"]


def reduce_header(elem, doc):
    if type(elem) == Header:
        cmd = "\\%s{" % sectionTypes[elem.level - 1]
        inlines = [RawInline(cmd, "tex")]
        inlines.extend(elem.content)
        inlines.append(RawInline("}", "tex"))
        return Plain(*inlines)


if __name__ == "__main__":
    run_filter(reduce_header)
