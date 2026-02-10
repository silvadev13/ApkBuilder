from .model import ViewNode
from .parser import ANDROID_NS

A = f"{{{ANDROID_NS}}}"

def snake_to_camel(s):
    if "_" not in s:
        return s

    partes = [p for p in s.split("_") if p]
    if not partes:
        return ""

    if s.startswith("_"):
        return ''.join(p[0].upper() + p[1:] for p in partes)
    else:
        return partes[0] + ''.join(p[0].upper() + p[1:] for p in partes[1:])

def normalize_id(value):
    if not value:
        return None
    return value.split("/")[-1]

def bind_views(elem, child=False):
    view_id = normalize_id(elem.get(A + "id"))
    binding_id = None
    if not view_id and not child:
        view_id = "rootView"
    if view_id:
        binding_id = snake_to_camel(view_id)
    children = [
        bind_views(child, child=True)
        for child in elem
        if isinstance(child.tag, str)
    ]
    return ViewNode(elem.tag, view_id, binding_id, children)