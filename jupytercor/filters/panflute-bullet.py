import panflute as pf

def action(elem, doc):
    if isinstance(elem, pf.BulletList):
        new_items = []
        for item in elem.content:
            item.content.extend([pf.Str('\n')])
            new_items.append(item)
            #new_items.append(pf.Str('\n'))
        return pf.BulletList(*new_items)

if __name__ == '__main__':
    pf.run_filter(action)