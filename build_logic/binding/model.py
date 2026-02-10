class ViewNode:
    def __init__(self, tag, view_id, binding_id, children):
        self.tag = tag
        self.view_id = view_id
        self.binding_id = binding_id
        self.children = children