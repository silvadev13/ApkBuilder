from .model import ViewNode
from .parser import parse_layout
from .resolver import bind_views
from ..core import get_logger
from ..project import Project
import os

DEFAULT_IMPORTS = {
    "android.view.LayoutInflater",
    "android.view.View",
    "android.view.ViewGroup",
    "android.widget.*"
}

def layout_to_binding_class_name(filename):
    name = filename.replace(".xml", "")
    parts = name.split("_")
    return "".join(p.capitalize() for p in parts) + "Binding"

def simple_tag(tag):
    if not tag:
        return None
    return tag.split(".")[-1]

def resolve_view_class(tag):
    if "." in tag:
        return tag
    return None

def infer_view_imports(views):
    imports = set(DEFAULT_IMPORTS)
    
    for v in views:
        tag = v.tag
        view_class = resolve_view_class(tag)
        if not view_class:
            continue
        
        if view_class in imports:
            continue
        
        imports.add(view_class)
    
    return imports

def generate_header(package, imports):
    lines = []
    lines.append("// Generated file. Do not modify.")
    lines.append(f"package {package};\n")
    lines.append(f"import {package.replace(".databinding", "")}.R;")
    
    for imp in sorted(imports):
        lines.append(f"import {imp};")
    lines.append("")
    
    return "\n".join(lines)

def collect_views(node, out):
    if node.view_id:
        out.append(node)
    for c in node.children:
        collect_views(c, out)

def generate_fields(views):
    lines = []
    for v in views:
        lines.append(
            f"    public final {simple_tag(v.tag)} {v.binding_id};"
        )
    lines.append("")
    return "\n".join(lines)

def generate_constructor(class_name, views):
    args = ", ".join(f"{simple_tag(v.tag)} {v.binding_id}" for v in views)
    lines = []
    lines.append(f"    private {class_name}({args}) " + "{")
    lines.append("\n".join(f"        this.{v.binding_id} = {v.binding_id};" for v in views))
    lines.append("    }\n")
    return "\n".join(lines)

def generate_get_root(root_type, root_field):
    return (
        f"    public {simple_tag(root_type)} getRoot() {{\n"
        f"        return {root_field};\n"
        f"    }}\n"
    )

def generate_inflate_methods(class_name, layout_name):
    lines = []

    lines.append(
        f"    public static {class_name} inflate(LayoutInflater inflater) {{"
    )
    lines.append(
        f"        return inflate(inflater, null, false);"
    )
    lines.append("    }\n")

    lines.append(
        f"    public static {class_name} inflate(LayoutInflater inflater, ViewGroup parent, boolean attachToParent) {{"
    )
    lines.append(
        f"        View root = inflater.inflate(R.layout.{layout_name}, parent, false);"
    )
    lines.append(
        f"        if (attachToParent) parent.addView(root);"
    )
    lines.append(
        f"        return bind(root);"
    )
    lines.append("    }\n")

    return "\n".join(lines)

def generate_bind(class_name, root_type, root_id, views):
    lines = []

    lines.append(f"    public static {class_name} bind(View view) {{")
    lines.append(
        f"        {simple_tag(root_type)} {root_id} = ({simple_tag(root_type)}) view;"
    )

    for v in views:
        class_view = simple_tag(v.tag)
        lines.append(
            f"        {class_view} {v.binding_id} = findChildViewById(view, R.id.{v.view_id});"
        )

    if views:
        checks = " || ".join(f"{v.binding_id} == null" for v in views)
        lines.append("")
        lines.append(f"        if ({checks}) {{")
        lines.append(
            '            throw new IllegalStateException("Required views are missing");'
        )
        lines.append("        }")
        lines.append("")

        args = ", ".join(v.binding_id for v in views)
        lines.append(f"        return new {class_name}({root_id}, {args});")
    else:
        lines.append("")
        lines.append(f"        return new {class_name}({root_id});")

    lines.append("    }")

    return "\n".join(lines)

def generate_find_child():
    return (
        "    private static <T extends View> T findChildViewById(View rootView, int id) {\n"
        "        if (rootView instanceof ViewGroup) {\n"
        "            ViewGroup rootViewGroup = (ViewGroup) rootView;\n"
        "            for (int i = 0; i < rootViewGroup.getChildCount(); i++) {\n"
        "                T view = rootViewGroup.getChildAt(i).findViewById(id);\n"
        "                if (view != null) return view;\n"
        "            }\n"
        "        }\n"
        "        return null;\n"
        "    }\n"
    )

def generate_binding_code(package, class_name, layout_name, root_node):
    views = []
    collect_views(root_node, views)

    imports = infer_view_imports(views)

    lines = []
    lines.append(generate_header(package, imports))
    lines.append(f"public final class {class_name} {{\n")

    lines.append(generate_fields(views))
    lines.append(generate_constructor(class_name, views))
    lines.append(generate_get_root(root_node.tag, root_node.binding_id))
    lines.append(generate_inflate_methods(class_name, layout_name))
    lines.append(generate_bind(class_name, root_node.tag, root_node.view_id, views[1:]))
    lines.append(generate_find_child())

    lines.append("}")
    return "\n".join(lines)

class GenerateViewBinding:
    def __init__(self, project: Project):
        self.project = project
    
    def prepare(self):
        pass
    
    def start(self):
        os.makedirs(self.project.get_view_binding_dir(), exist_ok=True)
        
        if not self.project.get_package_name():
            error_msg = "Attribute 'package' not found in AndroidManifest.xml, please, add"
            get_logger().error(error_msg)
            raise Exception(error_msg)
        
        get_logger().info("> :app:xmlToBinding")
        
        package_name = self.project.get_package_name() + ".databinding"
        output_dir = os.path.join(self.project.get_view_binding_dir(), package_name.replace(".", "/"))
        os.makedirs(output_dir, exist_ok=True)
        
        root = os.path.join(self.project.get_res_dir(), "layout")
        for f in os.listdir(root):
            full = os.path.join(root, f)
            if not full.endswith(".xml"):
                continue
            
            root_xml = parse_layout(full)
            root_node = bind_views(root_xml)
            
            layout_name = os.path.basename(full).replace(".xml", "")
            class_name = layout_to_binding_class_name(layout_name)
            
            binding_code = generate_binding_code(package_name, class_name, layout_name, root_node)
            
            with open(os.path.join(output_dir, f"{class_name}.java"), "w", encoding="utf-8") as f:
                f.write(binding_code)