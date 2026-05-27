from __future__ import annotations

import ast
import os
import pathlib
import re


def unparse(node):
    return ast.unparse(node)


def sig_from_funcdef(node, indent=""):
    """Generate a single-line stub method signature from a FunctionDef node."""
    parts = []
    for i, arg in enumerate(node.args.args):
        a = arg.arg
        if arg.annotation:
            a += f": {unparse(arg.annotation)}"
        parts.append(a)
    if node.args.vararg:
        a = "*" + node.args.vararg.arg
        if node.args.vararg.annotation:
            a += f": {unparse(node.args.vararg.annotation)}"
        parts.append(a)
    for arg in node.args.kwonlyargs:
        a = arg.arg
        if arg.annotation:
            a += f": {unparse(arg.annotation)}"
        parts.append(a)
    if node.args.kwarg:
        a = "**" + node.args.kwarg.arg
        if node.args.kwarg.annotation:
            a += f": {unparse(node.args.kwarg.annotation)}"
        parts.append(a)
    sig = f"def {node.name}({', '.join(parts)})"
    if node.returns:
        sig += f" -> {unparse(node.returns)}"
    sig += ": ..."
    return sig


# Known method signatures for builtin method aliases
_KNOWN_METHOD_SIGS = {
    ("str", "__format__"): "def __format__(self, __format_spec: str) -> str: ...",
    ("str", "__str__"): "def __str__(self) -> str: ...",
}


def method_alias_stub(attr_name, value_node):
    """Detect class-level method aliases (__format__ = str.__format__) -> method stub."""
    if isinstance(value_node, ast.Attribute) and isinstance(value_node.value, ast.Name):
        key = (value_node.value.id, value_node.attr)
        if key in _KNOWN_METHOD_SIGS:
            return _KNOWN_METHOD_SIGS[key]
    return None


# ---------------------------------------------------------------------------
# Type inference helpers
# ---------------------------------------------------------------------------


def infer_type_from_value(value_node, enum_classes):
    """
    Infer a type annotation string for a module-level assignment's value.
    Returns None if the type cannot be determined.
    For type-expression-like values (Callable, Union, etc.), returns a
    sentinel dict with key 'type_alias' containing the full expression.
    """
    if isinstance(value_node, ast.Constant):
        return {
            str: "str",
            int: "int",
            float: "float",
            bool: "bool",
            bytes: "bytes",
        }.get(type(value_node.value))

    # EnumClass.MEMBER -> int
    if isinstance(value_node, ast.Attribute):
        if (
            isinstance(value_node.value, ast.Name)
            and value_node.value.id in enum_classes
        ):
            return "int"
        # Generic ClassName.MEMBER -> ClassName (for enums, constants etc.)
        if isinstance(value_node.value, ast.Name) and value_node.value.id[0].isupper():
            return value_node.value.id

    if isinstance(value_node, ast.Call):
        f = value_node.func
        # str(x), repr(x), format(x) -> str
        if isinstance(f, ast.Name) and f.id in ("str", "repr", "format"):
            return "str"
        # int(x) -> int
        if isinstance(f, ast.Name) and f.id == "int":
            return "int"
        # bool(x) -> bool
        if isinstance(f, ast.Name) and f.id == "bool":
            return "bool"
        # float(x) -> float
        if isinstance(f, ast.Name) and f.id == "float":
            return "float"
        # bytes(x) -> bytes
        if isinstance(f, ast.Name) and f.id == "bytes":
            return "bytes"
        # list() -> list, dict() -> dict, set() -> set, tuple() -> tuple
        if isinstance(f, ast.Name) and f.id in ("list", "dict", "set", "tuple"):
            return f.id
        # os.path.join/dirname/etc -> str
        if (
            isinstance(f, ast.Attribute)
            and isinstance(f.value, ast.Attribute)
            and isinstance(f.value.value, ast.Name)
            and f.value.value.id == "os"
            and f.value.attr == "path"
        ):
            # Check if the final attribute is a path function
            if f.attr in (
                "join",
                "dirname",
                "basename",
                "abspath",
                "realpath",
                "splitext",
                "split",
                "exists",
                "isfile",
                "isdir",
            ):
                return "str"
        # sublime.load_resource(...) -> str
        if (
            isinstance(f, ast.Attribute)
            and isinstance(f.value, ast.Name)
            and f.value.id == "sublime"
            and f.attr in ("load_resource", "load_settings", "get_clipboard")
        ):
            return "str"
        # Callable[[...], ...] -> type alias
        if isinstance(f, ast.Name) and f.id == "Callable":
            return {"type_alias": unparse(value_node)}
        # Union[...], Optional[...] -> type alias
        if isinstance(f, ast.Name) and f.id in ("Union", "Optional"):
            return {"type_alias": unparse(value_node)}
        # TypeVar(...) -> keep as alias
        if isinstance(f, ast.Name) and f.id == "TypeVar":
            return {"type_alias": unparse(value_node)}
        # NamedTuple(...) -> keep as alias
        if isinstance(f, ast.Name) and f.id == "NamedTuple":
            return {"type_alias": unparse(value_node)}
        # TypedDict(...) -> keep as alias
        if isinstance(f, ast.Name) and f.id == "TypedDict":
            return {"type_alias": unparse(value_node)}
        # NewType(...) -> keep
        if isinstance(f, ast.Name) and f.id == "NewType":
            return {"type_alias": unparse(value_node)}
        # any(...) / all(...) -> bool
        if isinstance(f, ast.Name) and f.id in ("any", "all"):
            return "bool"
        # Generic constructor call: ClassName(...) -> ClassName
        if isinstance(f, ast.Name) and f.id[0].isupper():
            return f.id
        # Known lowercase constructors
        if isinstance(f, ast.Name) and f.id in ("timedelta", "defaultdict"):
            return f.id
        # set() call but with a generator/comprehension arg -> set[T]
        if isinstance(f, ast.Name) and f.id == "set":
            if value_node.args or value_node.keywords:
                return "set"
            return "set"

    if isinstance(value_node, ast.JoinedStr):
        return "str"

    if isinstance(value_node, ast.Dict):
        return "dict"

    if isinstance(value_node, ast.IfExp):
        # 10000 if CI else 2000  ->  int
        bt = infer_type_from_value(value_node.body, enum_classes)
        ot = infer_type_from_value(value_node.orelse, enum_classes)
        if isinstance(bt, str) and bt == ot:
            return bt
        return None

    if isinstance(value_node, ast.BinOp) and isinstance(value_node.op, ast.BitOr):
        # WatchKind.A | WatchKind.B  ->  WatchKind
        if (
            isinstance(value_node.left, ast.Attribute)
            and isinstance(value_node.right, ast.Attribute)
            and isinstance(value_node.left.value, ast.Name)
            and isinstance(value_node.right.value, ast.Name)
            and value_node.left.value.id == value_node.right.value.id
        ):
            return value_node.left.value.id
        # Recurse into nested BinOp
        lt = infer_type_from_value(value_node.left, enum_classes)
        rt = infer_type_from_value(value_node.right, enum_classes)
        if isinstance(lt, str) and lt == rt:
            return lt

    if isinstance(value_node, ast.BinOp) and isinstance(value_node.op, ast.Add):
        lt = infer_type_from_value(value_node.left, enum_classes)
        rt = infer_type_from_value(value_node.right, enum_classes)
        if lt is not None and lt == rt and isinstance(lt, str):
            return lt

    # Subscript: List[int], Dict[str, Any] -> type alias.
    # CONFIGURATION['key'] is a runtime subscript, not a type alias.
    if isinstance(value_node, ast.Subscript):
        # String subscript (CONFIGURATION['key']) is runtime, not type
        if isinstance(value_node.slice, ast.Constant) and isinstance(
            value_node.slice.value, str
        ):
            return None
        return {"type_alias": unparse(value_node)}

    # NamedExpr (walrus operator) -> try inferring the value
    if isinstance(value_node, ast.NamedExpr):
        return infer_type_from_value(value_node.value, enum_classes)

    return None


# ---------------------------------------------------------------------------
# Source info collection
# ---------------------------------------------------------------------------


def collect_source_info(src_path):
    """Collect type-relevant info from a source file."""
    try:
        tree = ast.parse(
            pathlib.Path(src_path).read_text(encoding="utf-8", errors="replace")
        )
    except SyntaxError:
        return None

    info = {
        "annotations": {},  # name -> type_str
        "type_aliases": {},  # name -> " = expr"
        "type_aliases_line": {},  # name -> "name = expr"
        "class_attrs": {},  # class -> {attr: type_str} (from AnnAssign + __init__)
        "class_methods": {},  # class -> {method: stub_sig}
        "enum_member_names": {},  # class -> {member: True}
        "import_nodes": [],
    }

    # Phase 1: identify IntEnum/IntFlag
    enum_classes = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                bname = (
                    base.id
                    if isinstance(base, ast.Name)
                    else base.attr
                    if isinstance(base, ast.Attribute)
                    else None
                )
                if bname in ("IntEnum", "IntFlag"):
                    enum_classes.add(node.name)

    # Helper to process a single class body (works for top-level and nested classes)
    def _collect_class_body(class_node, is_enum, info):
        ca, cm, ce = {}, {}, set()
        for item in ast.iter_child_nodes(class_node):
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                ca[item.target.id] = unparse(item.annotation)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if is_enum:
                            ce.add(target.id)
                        inferred = infer_type_from_value(item.value, enum_classes)
                        if isinstance(inferred, str) and target.id not in ca:
                            ca[target.id] = inferred
                        alias_method = method_alias_stub(target.id, item.value)
                        if alias_method and target.id not in cm:
                            cm[target.id] = alias_method
            elif isinstance(item, ast.FunctionDef):
                stub = sig_from_funcdef(item)
                if item.name == "__init__":
                    init_params = {}
                    for arg in item.args.args:
                        if arg.arg != "self" and arg.annotation:
                            init_params[arg.arg] = unparse(arg.annotation)
                    for body_node in ast.walk(item):
                        if (
                            isinstance(body_node, ast.AnnAssign)
                            and isinstance(body_node.target, ast.Attribute)
                            and isinstance(body_node.target.value, ast.Name)
                            and body_node.target.value.id == "self"
                        ):
                            ca[body_node.target.attr] = unparse(body_node.annotation)
                        if (
                            isinstance(body_node, ast.Assign)
                            and len(body_node.targets) == 1
                            and isinstance(body_node.targets[0], ast.Attribute)
                            and isinstance(body_node.targets[0].value, ast.Name)
                            and body_node.targets[0].value.id == "self"
                        ):
                            attr = body_node.targets[0].attr
                            if attr in ca:
                                continue
                            val = body_node.value
                            if isinstance(val, ast.Name) and val.id in init_params:
                                ca[attr] = init_params[val.id]
                            elif (
                                isinstance(val, ast.Call)
                                and isinstance(val.func, ast.Name)
                                and len(val.args) == 1
                                and isinstance(val.args[0], ast.Name)
                                and val.args[0].id in init_params
                            ):
                                ca[attr] = (
                                    f"{val.func.id}[{init_params[val.args[0].id]}]"
                                )
                            elif (
                                isinstance(val, ast.Call)
                                and isinstance(val.func, ast.Attribute)
                                and isinstance(val.func.value, ast.Name)
                                and val.func.value.id == "weakref"
                                and val.func.attr == "ref"
                                and len(val.args) == 1
                                and isinstance(val.args[0], ast.Name)
                                and val.args[0].id in init_params
                            ):
                                ca[attr] = f"ref[{init_params[val.args[0].id]}]"
                            # Pattern D: self.attr = literal (str, int, bool, etc.)
                            else:
                                lit_type = infer_type_from_value(val, enum_classes)
                                if isinstance(lit_type, str):
                                    ca[attr] = lit_type
                else:
                    cm[item.name] = stub
        if ca:
            info["class_attrs"][class_node.name] = ca
        if cm:
            info["class_methods"][class_node.name] = cm
        if ce:
            info["enum_member_names"][class_node.name] = ce

    # Phase 3: collect info from class definitions (all depths via ast.walk)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            _collect_class_body(node, node.name in enum_classes, info)

    # Phase 4: collect module-level info (imports, annotations, aliases)
    for node in ast.iter_child_nodes(tree):
        # Module-level annotation
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            info["annotations"][node.target.id] = unparse(node.annotation)

        # Module-level assignment (candidates: type alias or inferred type)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # __version__ is conventionally str
                    if target.id == "__version__":
                        info["annotations"][target.id] = "str"
                    else:
                        inferred = infer_type_from_value(node.value, enum_classes)
                        if isinstance(inferred, dict) and "type_alias" in inferred:
                            expr = inferred["type_alias"]
                            info["type_aliases"][target.id] = f" = {expr}"
                            info["type_aliases_line"][target.id] = (
                                f"{target.id} = {expr}"
                            )
                        elif isinstance(inferred, str):
                            info["annotations"][target.id] = inferred

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            info["import_nodes"].append(node)

    # Phase 3: collect info from class definitions (all depths via ast.walk)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            _collect_class_body(node, node.name in enum_classes, info)

    return info


# ---------------------------------------------------------------------------
# Fix application
# ---------------------------------------------------------------------------


def apply_fixes(txt, info):
    """Apply type fixes to stub text using collected source info."""
    lines = txt.split("\n")
    new_lines = []
    # Track class context: list of class names by indent level
    class_at_indent = {}  # indent_str -> class_name

    for raw in lines:
        stripped = raw.lstrip()
        indent = raw[: len(raw) - len(stripped)]

        # Track class boundaries
        cm = re.match(r"^(\s*)class (\w+)", raw)
        if cm:
            cls_indent = cm.group(1)
            cls_name = cm.group(2)
            # Remove any inner classes at this or deeper indent
            keys = [k for k in class_at_indent if len(k) >= len(cls_indent)]
            for k in keys:
                del class_at_indent[k]
            class_at_indent[cls_indent] = cls_name
            new_lines.append(raw)
            continue

        # Check for Incomplete pattern
        m = re.match(r"^(\s*)([A-Za-z_]\w*): Incomplete\s*$", raw)
        if not m:
            new_lines.append(raw)
            continue

        name = m.group(2)
        name_indent = m.group(1)

        # Find current class: the closest class at a shallower indent level
        current_class = None
        ci = None
        for ci in sorted(class_at_indent.keys(), key=len, reverse=True):
            if len(name_indent) > len(ci):
                current_class = class_at_indent[ci]
                break

        replaced = False

        # --- Module-level fixes ---
        if current_class is None:
            if name in info.get("annotations", {}):
                new_lines.append(f"{indent}{name}: {info['annotations'][name]}")
                replaced = True
            elif name in info.get("type_aliases", {}):
                new_lines.append(f"{indent}{info['type_aliases_line'][name]}")
                replaced = True
            elif name in info.get("top_level_functions", {}):
                pass  # handled by func_restore below
                # fall through to no-replace

        # --- Class-level fixes ---
        if not replaced and current_class:
            # Class annotations
            if current_class in info.get("class_attrs", {}):
                if name in info["class_attrs"][current_class]:
                    new_lines.append(
                        f"{indent}{name}: {info['class_attrs'][current_class][name]}"
                    )
                    replaced = True
            # Class methods (e.g. __format__)
            if not replaced and current_class in info.get("class_methods", {}):
                if name in info["class_methods"][current_class]:
                    new_lines.append(
                        f"{indent}{info['class_methods'][current_class][name]}"
                    )
                    replaced = True
            # Enum members
            if not replaced and current_class in info.get("enum_member_names", {}):
                if name in info["enum_member_names"][current_class]:
                    new_lines.append(f"{indent}{name}: int")
                    replaced = True

        if not replaced:
            new_lines.append(raw)

    return "\n".join(new_lines)


# ---------------------------------------------------------------------------
# Import management
# ---------------------------------------------------------------------------


def _get_imported_names(txt):
    """Return set of all names imported in the stub text."""
    names = set()
    for line in txt.split("\n"):
        line = line.strip()
        if line.startswith("import ") and not line.startswith("import_"):
            # import foo, bar
            rest = line[7:]
            for part in rest.split(","):
                part = part.strip().split()[0]  # handle 'import foo as bar'
                names.add(part.split()[0])
        elif line.startswith("from ") and " import " in line:
            # from foo import bar, baz
            imp_part = line.split(" import ", 1)[1]
            for part in imp_part.split(","):
                part = part.strip()
                alias = part.split(" as ")
                names.add(alias[0].strip())
    return names


def add_missing_imports(txt, info):
    """Add imports from source that are needed but missing."""
    existing_names = _get_imported_names(txt)
    existing_set = set(txt.split("\n"))
    lines = txt.split("\n")

    _NEVER = {"from __future__ import annotations", "from _typeshed import Incomplete"}

    def build_import(module, names, level):
        return ast.unparse(ast.ImportFrom(module=module, names=names, level=level))

    needed = []
    for imp_node in info.get("import_nodes", []):
        if isinstance(imp_node, ast.Import):
            line = unparse(imp_node)
            if line not in existing_set and line not in _NEVER:
                for alias in imp_node.names:
                    name = alias.asname or alias.name
                    if name not in existing_names and re.search(
                        r"\b" + re.escape(name) + r"\.\s*\w", txt
                    ):
                        needed.append(line)
                        break
        elif isinstance(imp_node, ast.ImportFrom):
            line = unparse(imp_node)
            if line in existing_set or line in _NEVER:
                continue
            missing = []
            for alias in imp_node.names:
                name = alias.asname or alias.name
                if name not in existing_names:
                    stripped = re.sub(r"#.*", "", txt)
                    if re.search(
                        r"(?<![a-zA-Z_.])" + re.escape(name) + r"(?![a-zA-Z_])",
                        stripped,
                    ):
                        missing.append(alias)
            if missing:
                if len(missing) < len(imp_node.names):
                    narrow = build_import(imp_node.module, missing, imp_node.level)
                else:
                    narrow = line
                needed.append(narrow)

    if not needed:
        return txt

    # Insert after the last import line
    last_import_idx = -1
    for i, l in enumerate(lines):
        if l.startswith(("import ", "from ")):
            last_import_idx = i
    insert_idx = last_import_idx + 1

    for imp in needed:
        if imp not in existing_set and imp not in _NEVER:
            lines.insert(insert_idx, imp)
            existing_set.add(imp)
            insert_idx += 1

    txt = "\n".join(lines)
    while "\n\n\n" in txt:
        txt = txt.replace("\n\n\n", "\n\n")
    return txt


def cleanup_incomplete_import(txt):
    """Remove _typeshed import if no Incomplete markers remain."""
    if ": Incomplete" not in txt:
        txt = re.sub(
            r"^from _typeshed import Incomplete\n",
            "",
            txt,
            flags=re.MULTILINE,
        )
        txt = re.sub(r"\n{3,}", "\n\n", txt)
        txt = re.sub(r"^\n+", "", txt)
    return txt


# ---- Main ----
out = pathlib.Path(os.environ["LSP_OUT"])
lsp_src = pathlib.Path(os.environ["LSP_SRC"])

for pyi in sorted(out.rglob("*.pyi")):
    txt = pyi.read_bytes().decode("utf-8").replace("\r\n", "\n")

    if ": Incomplete" not in txt:
        continue

    # Locate source using relative path first, then fallbacks
    rel = pyi.relative_to(out)
    src = None
    for ext in (".pyi", ".py"):
        candidate = lsp_src / rel.with_suffix(ext)
        if candidate.exists():
            src = candidate
            break
    if src is None:
        for ext in (".pyi", ".py"):
            candidate = lsp_src / (pyi.stem + ext)
            if candidate.exists():
                src = candidate
                break
    if src is None:
        for ext in (".pyi", ".py"):
            found = next(lsp_src.rglob(pyi.stem + ext), None)
            if found:
                src = found
                break

    if src:
        info = collect_source_info(src)
        if info:
            txt = apply_fixes(txt, info)
            txt = add_missing_imports(txt, info)
            txt = cleanup_incomplete_import(txt)

    pyi.write_bytes(txt.encode("utf-8"))
