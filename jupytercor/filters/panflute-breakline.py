import panflute as pf


def action(elem, doc):
    if isinstance(elem, pf.Image):
        return [pf.LineBreak(), elem, pf.LineBreak(), pf.LineBreak()]
    else:
        return None


if __name__ == "__main__":
    pf.run_filter(action)
