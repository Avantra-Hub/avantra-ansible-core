from __future__ import (absolute_import, division, print_function)

import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
from collections import defaultdict


def _etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(_etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def xmldict(xml):
    it = ET.iterparse(StringIO(xml.decode("UTF-8")))
    for _, el in it:
        _, _, el.tag = el.tag.rpartition('}')  # strip ns
    root = it.root
    return _etree_to_dict(root)
