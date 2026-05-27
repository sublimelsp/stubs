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
        # module.ClassName.MEMBER -> module.ClassName (e.g. sublime.RegionFlags.X)
        if (
            isinstance(value_node.value, ast.Attribute)
            and isinstance(value_node.value.value, ast.Name)
            and value_node.value.attr[0].isupper()
        ):
            return f"{value_node.value.value.id}.{value_node.value.attr}"

    if isinstance(value_node, ast.Call):
        f = value_node.func
        # str(x), repr(x), format(x) -> str
        if isinstance(f, ast.Name) and f.id in ("str", "repr", "format"):
            return "str"
        # cast("TypeName", value) or cast(TypeName, value) -> TypeName
        if isinstance(f, ast.Name) and f.id == "cast" and len(value_node.args) >= 1:
            first = value_node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                return first.value
            if isinstance(first, (ast.Name, ast.Subscript, ast.Attribute)):
                return unparse(first)
        # "str".method(...) -> str (format, join, strip, etc.)
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Constant) and isinstance(f.value.value, str):
            if f.attr in ("format", "join", "strip", "lstrip", "rstrip", "upper", "lower", "replace", "format_map"):
                return "str"
            if f.attr == "encode":
                return "bytes"
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
        # Bare os.path functions imported directly: join(), dirname(), etc. -> str
        if isinstance(f, ast.Name) and f.id in (
            "join", "dirname", "basename", "abspath", "realpath",
        ):
            return "str"
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
        # sublime.*() calls -> str
        if (
            isinstance(f, ast.Attribute)
            and isinstance(f.value, ast.Name)
            and f.value.id == "sublime"
            and f.attr in (
                "load_resource", "load_settings", "get_clipboard",
                "cache_path", "packages_path", "installed_packages_path",
                "platform", "version", "executable_path", "executable_hash",
            )
        ):
            return "str"
        # re.compile(...) -> re.Pattern[str]
        if (
            isinstance(f, ast.Attribute)
            and isinstance(f.value, ast.Name)
            and f.value.id == "re"
            and f.attr == "compile"
        ):
            return "re.Pattern[str]"
        # json.loads(...) -> Any  (parsed JSON has no static type)
        if (
            isinstance(f, ast.Attribute)
            and isinstance(f.value, ast.Name)
            and f.value.id == "json"
            and f.attr == "loads"
        ):
            return "Any"
        # logging.getLogger(...) -> logging.Logger
        if (
            isinstance(f, ast.Attribute)
            and isinstance(f.value, ast.Name)
            and f.value.id == "logging"
            and f.attr == "getLogger"
        ):
            return "logging.Logger"
        # getattr(obj, attr, default) -> type of default
        if isinstance(f, ast.Name) and f.id == "getattr" and len(value_node.args) >= 3:
            return infer_type_from_value(value_node.args[2], enum_classes)
        # obj.get(key, default) -> type of default
        if isinstance(f, ast.Attribute) and f.attr == "get" and len(value_node.args) >= 2:
            return infer_type_from_value(value_node.args[1], enum_classes)
        # obj.get(key) -> Any  (no default, could be None or the dict value type)
        if isinstance(f, ast.Attribute) and f.attr == "get" and len(value_node.args) == 1:
            return "Any"
        # module.ClassName(...) -> module.ClassName (e.g. threading.Lock())
        if (
            isinstance(f, ast.Attribute)
            and isinstance(f.value, ast.Name)
            and f.attr[0].isupper()
        ):
            return f"{f.value.id}.{f.attr}"
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
        if not value_node.keys:
            return "dict"
        key_types = set()
        val_types = set()
        for k, v in zip(value_node.keys, value_node.values):
            if k is None:  # dict unpacking **other
                return "dict"
            kt = infer_type_from_value(k, enum_classes)
            vt = infer_type_from_value(v, enum_classes)
            key_types.add(kt if isinstance(kt, str) else None)
            val_types.add(vt if isinstance(vt, str) else None)
        k_unified = next(iter(key_types)) if len(key_types) == 1 and None not in key_types else None
        v_unified = next(iter(val_types)) if len(val_types) == 1 and None not in val_types else None
        if k_unified and v_unified:
            return f"dict[{k_unified}, {v_unified}]"
        return "dict"

    if isinstance(value_node, ast.List):
        if not value_node.elts:
            return "list"
        elt_types = set()
        for e in value_node.elts:
            et = infer_type_from_value(e, enum_classes)
            elt_types.add(et if isinstance(et, str) else None)
        if len(elt_types) == 1 and None not in elt_types:
            return f"list[{next(iter(elt_types))}]"
        return "list"

    if isinstance(value_node, ast.Set):
        if not value_node.elts:
            return "set"
        elt_types = set()
        for e in value_node.elts:
            et = infer_type_from_value(e, enum_classes)
            elt_types.add(et if isinstance(et, str) else None)
        if len(elt_types) == 1 and None not in elt_types:
            return f"set[{next(iter(elt_types))}]"
        return "set"

    if isinstance(value_node, ast.ListComp):
        elt_type = infer_type_from_value(value_node.elt, enum_classes)
        if isinstance(elt_type, str):
            return f"list[{elt_type}]"
        return "list"

    if isinstance(value_node, ast.SetComp):
        elt_type = infer_type_from_value(value_node.elt, enum_classes)
        if isinstance(elt_type, str):
            return f"set[{elt_type}]"
        return "set"

    if isinstance(value_node, ast.DictComp):
        k_type = infer_type_from_value(value_node.key, enum_classes)
        v_type = infer_type_from_value(value_node.value, enum_classes)
        if isinstance(k_type, str) and isinstance(v_type, str):
            return f"dict[{k_type}, {v_type}]"
        return "dict"

    if isinstance(value_node, ast.Tuple):
        if not value_node.elts:
            return "tuple[()]"
        elt_types_list = [
            infer_type_from_value(e, enum_classes) for e in value_node.elts
        ]
        if all(isinstance(t, str) for t in elt_types_list):
            return f"tuple[{', '.join(elt_types_list)}]"  # type: ignore[arg-type]
        return "tuple"

    if isinstance(value_node, ast.IfExp):
        # 10000 if CI else 2000  ->  int
        bt = infer_type_from_value(value_node.body, enum_classes)
        ot = infer_type_from_value(value_node.orelse, enum_classes)
        if isinstance(bt, str) and bt == ot:
            return bt
        # T if cond else None  ->  T | None
        if (
            isinstance(bt, str)
            and isinstance(value_node.orelse, ast.Constant)
            and value_node.orelse.value is None
        ):
            return f"{bt} | None"
        return None

    if isinstance(value_node, ast.BoolOp) and isinstance(value_node.op, ast.Or):
        # x or y: if all values share a type return it; otherwise fall back to last value's type
        inferred_types = [infer_type_from_value(v, enum_classes) for v in value_node.values]
        str_types = [t for t in inferred_types if isinstance(t, str)]
        if str_types and all(t == str_types[0] for t in str_types) and len(str_types) == len(inferred_types):
            return str_types[0]
        if str_types and isinstance(inferred_types[-1], str):
            return inferred_types[-1]

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

    if isinstance(value_node, ast.BinOp) and isinstance(value_node.op, ast.Mult):
        lt = infer_type_from_value(value_node.left, enum_classes)
        rt = infer_type_from_value(value_node.right, enum_classes)
        # "str" * int or int * "str" -> str
        if (lt == "str" and rt == "int") or (lt == "int" and rt == "str"):
            return "str"
        if lt == "int" and rt == "int":
            return "int"

    if isinstance(value_node, ast.BinOp) and isinstance(
        value_node.op, (ast.Sub, ast.Pow, ast.FloorDiv, ast.Mod)
    ):
        lt = infer_type_from_value(value_node.left, enum_classes)
        rt = infer_type_from_value(value_node.right, enum_classes)
        if lt == "int" and rt == "int":
            return "int"

    # Subscript: distinguish type expressions (list[int]) from runtime subscripts (func()[0]).
    if isinstance(value_node, ast.Subscript):
        # func()[n] is always runtime
        if isinstance(value_node.value, ast.Call):
            return "Any"
        # Name subscript: could be type (list[int]) or runtime (var[0])
        if isinstance(value_node.value, ast.Name):
            name = value_node.value.id
            if name[0].isupper() or name in {"list", "dict", "set", "tuple", "type", "frozenset"}:
                if isinstance(value_node.slice, ast.Constant) and isinstance(value_node.slice.value, str):
                    return None  # TypeName['key'] is a runtime access, not a type expression
                return {"type_alias": unparse(value_node)}
            return "Any"  # lowercase name subscript is runtime
        # Attribute subscript: typing.Dict[str, Any] vs self.attr[0] / module.attr[n]
        if isinstance(value_node.value, ast.Attribute):
            if isinstance(value_node.value.value, ast.Name) and value_node.value.value.id == "self":
                return "Any"  # self.attr[n] is runtime
            if value_node.value.attr[0].isupper():
                if isinstance(value_node.slice, ast.Constant) and isinstance(value_node.slice.value, str):
                    return None
                return {"type_alias": unparse(value_node)}
            return "Any"
        # Nested subscript: generic[T, list[int]]
        if isinstance(value_node.value, ast.Subscript):
            return {"type_alias": unparse(value_node)}
        return "Any"

    # NamedExpr (walrus operator) -> try inferring the value
    if isinstance(value_node, ast.NamedExpr):
        return infer_type_from_value(value_node.value, enum_classes)

    return None


# ---------------------------------------------------------------------------
# Source info collection
# ---------------------------------------------------------------------------


def collect_source_info(src_path, baseline=None):
    """Collect type-relevant info from a source file."""
    try:
        tree = ast.parse(
            pathlib.Path(src_path).read_text(encoding="utf-8", errors="replace")
        )
    except SyntaxError:
        return None

    info = {
        "annotations": {},  # name -> type_str
        "type_aliases": {},  # name -> " = expr"  (from plain assignments)
        "type_aliases_line": {},  # name -> "name = expr"  (from plain assignments)
        "annotated_type_aliases": {},  # name -> value_str  (from `Name: TypeAlias = ...`)
        "class_attrs": {},  # class -> {attr: type_str} (from AnnAssign + __init__)
        "class_methods": {},  # class -> {method: stub_sig}
        "enum_member_names": {},  # class -> {member: True}
        "narrowed_class_attrs": {},  # class -> {attr: type_str} narrowed from T | None -> T
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
        ca, cm, ce, narrowed = {}, {}, set(), {}
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
                    for arg in item.args.args + item.args.kwonlyargs:
                        if arg.arg != "self":
                            init_params[arg.arg] = unparse(arg.annotation) if arg.annotation else "Any"
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
                            # Pattern E: self.attr = param or default
                            # The `or default` guarantees the result is non-None, so
                            # strip any trailing `| None` from the param type.
                            elif (
                                isinstance(val, ast.BoolOp)
                                and isinstance(val.op, ast.Or)
                                and val.values
                                and isinstance(val.values[0], ast.Name)
                                and val.values[0].id in init_params
                            ):
                                param_type = init_params[val.values[0].id]
                                if param_type.endswith(" | None"):
                                    stripped = param_type[: -len(" | None")]
                                    ca[attr] = stripped
                                    narrowed[attr] = stripped
                                elif param_type.startswith("None | "):
                                    stripped = param_type[len("None | "):]
                                    ca[attr] = stripped
                                    narrowed[attr] = stripped
                                else:
                                    ca[attr] = param_type
                            # Pattern F: self.attr = param.some_attr (attribute of typed param)
                            elif (
                                isinstance(val, ast.Attribute)
                                and isinstance(val.value, ast.Name)
                                and val.value.id in init_params
                            ):
                                param_type = init_params[val.value.id]
                                attr_type = (
                                    info.get("class_attrs", {})
                                    .get(param_type, {})
                                    .get(val.attr)
                                )
                                if attr_type:
                                    ca[attr] = attr_type
                            # Pattern H: self.attr = param['key'] (subscript on typed init param)
                            elif (
                                isinstance(val, ast.Subscript)
                                and isinstance(val.value, ast.Name)
                                and val.value.id in init_params
                            ):
                                ca[attr] = "Any"
                            # Pattern D: self.attr = literal (str, int, bool, etc.)
                            else:
                                lit_type = infer_type_from_value(val, enum_classes)
                                if isinstance(lit_type, str):
                                    ca[attr] = lit_type
                else:
                    cm[item.name] = stub
                    # @property → also record return type as a class attribute
                    is_property = any(
                        isinstance(d, ast.Name) and d.id == "property"
                        for d in item.decorator_list
                    )
                    if is_property and item.returns and item.name not in ca:
                        ca[item.name] = unparse(item.returns)
                    # Scan non-__init__ methods for typed self-attribute assignments
                    for body_node in ast.walk(item):
                        if (
                            isinstance(body_node, ast.AnnAssign)
                            and isinstance(body_node.target, ast.Attribute)
                            and isinstance(body_node.target.value, ast.Name)
                            and body_node.target.value.id == "self"
                        ):
                            attr = body_node.target.attr
                            if attr not in ca:
                                ca[attr] = unparse(body_node.annotation)
                        elif (
                            isinstance(body_node, ast.Assign)
                            and len(body_node.targets) == 1
                            and isinstance(body_node.targets[0], ast.Attribute)
                            and isinstance(body_node.targets[0].value, ast.Name)
                            and body_node.targets[0].value.id == "self"
                        ):
                            attr = body_node.targets[0].attr
                            if attr not in ca:
                                val = body_node.value
                                # self.attr = cast(Type, ...) -> Type
                                if (
                                    isinstance(val, ast.Call)
                                    and isinstance(val.func, ast.Name)
                                    and val.func.id == "cast"
                                    and len(val.args) >= 1
                                ):
                                    first = val.args[0]
                                    if isinstance(first, ast.Constant) and isinstance(first.value, str):
                                        ca[attr] = first.value
                                    elif isinstance(first, (ast.Name, ast.Subscript, ast.Attribute)):
                                        ca[attr] = unparse(first)
        if ca:
            info["class_attrs"][class_node.name] = ca
        if cm:
            info["class_methods"][class_node.name] = cm
        if ce:
            info["enum_member_names"][class_node.name] = ce
        if narrowed:
            info["narrowed_class_attrs"][class_node.name] = narrowed

    # Phase 3: collect info from class definitions (all depths via ast.walk)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            _collect_class_body(node, node.name in enum_classes, info)

    # Phase 3.5: merge inherited class attrs from baseline (e.g. WindowCommand -> self.window)
    if baseline:
        baseline_class_attrs = baseline.get("class_attrs", {})
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for base in node.bases:
                base_name = (
                    base.id if isinstance(base, ast.Name)
                    else base.attr if isinstance(base, ast.Attribute)
                    else None
                )
                if base_name and base_name in baseline_class_attrs:
                    inherited = baseline_class_attrs[base_name]
                    existing = info.setdefault("class_attrs", {}).setdefault(node.name, {})
                    for attr, attr_type in inherited.items():
                        if attr not in existing:
                            existing[attr] = attr_type
        # Also merge all baseline class_attrs so Pattern F can resolve
        # param.attr lookups on sublime types (e.g. sublime.Window).
        for cls, attrs in baseline_class_attrs.items():
            if cls not in info["class_attrs"]:
                info["class_attrs"][cls] = dict(attrs)
            else:
                for attr, attr_type in attrs.items():
                    if attr not in info["class_attrs"][cls]:
                        info["class_attrs"][cls][attr] = attr_type

    # Phase 4: collect module-level info (imports, annotations, aliases)
    for node in ast.iter_child_nodes(tree):
        # Module-level annotation
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            ann = node.annotation
            is_type_alias_ann = (isinstance(ann, ast.Name) and ann.id == "TypeAlias") or (
                isinstance(ann, ast.Attribute) and ann.attr == "TypeAlias"
            )
            if is_type_alias_ann and node.value is not None:
                # `Name: TypeAlias = <value>` — store value so stubs can be completed
                info["annotated_type_aliases"][node.target.id] = unparse(node.value)
            else:
                ann_str = unparse(ann)
                # If the source annotation is a bare collection type but a value is
                # available, try to infer a more specific parameterized type from it.
                if ann_str in ("dict", "list", "set", "tuple") and node.value is not None:
                    inferred = infer_type_from_value(node.value, enum_classes)
                    if isinstance(inferred, str) and inferred.startswith(ann_str + "["):
                        ann_str = inferred
                info["annotations"][node.target.id] = ann_str

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

    # Phase 4.5a: propagate Any through subscripts/gets on Any-typed module-level vars
    # e.g. CONFIGURATION: Any -> RELEASE_BRANCH = CONFIGURATION['key'] -> Any
    any_vars = {k for k, v in info["annotations"].items() if v == "Any"}
    if any_vars:
        for node in ast.iter_child_nodes(tree):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if not isinstance(target, ast.Name) or target.id in info["annotations"]:
                    continue
                val = node.value
                # ANY_VAR['key'] -> Any
                if (
                    isinstance(val, ast.Subscript)
                    and isinstance(val.value, ast.Name)
                    and val.value.id in any_vars
                ):
                    info["annotations"][target.id] = "Any"
                # ANY_VAR.get(key, ...) -> Any
                elif (
                    isinstance(val, ast.Call)
                    and isinstance(val.func, ast.Attribute)
                    and isinstance(val.func.value, ast.Name)
                    and val.func.value.id in any_vars
                    and val.func.attr == "get"
                ):
                    info["annotations"][target.id] = "Any"
                # ANY_VAR['key'] or default -> type of default or Any
                elif (
                    isinstance(val, ast.BoolOp)
                    and isinstance(val.op, ast.Or)
                    and val.values
                    and isinstance(val.values[0], ast.Subscript)
                    and isinstance(val.values[0].value, ast.Name)
                    and val.values[0].value.id in any_vars
                ):
                    last_type = infer_type_from_value(val.values[-1], enum_classes)
                    info["annotations"][target.id] = last_type if isinstance(last_type, str) else "Any"

    # Phase 4.5b: resolve dependent types using collected annotations
    # e.g. SUPPORTED_DIAGNOSTIC_TAGS = list(DIAGNOSTIC_TAG_SCOPES)
    #      DIAGNOSTIC_TAG_SCOPES: dict[DiagnosticTag, str] -> list[DiagnosticTag]
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if info["annotations"].get(target.id) != "list":
                continue
            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "list"
                and len(node.value.args) == 1
                and isinstance(node.value.args[0], ast.Name)
            ):
                arg_type = info["annotations"].get(node.value.args[0].id, "")
                m = re.match(r"dict\[([^,\[\]]+),", arg_type)
                if m:
                    info["annotations"][target.id] = f"list[{m.group(1).strip()}]"

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

        # Check for bare `Name: TypeAlias` (stubgen drops the value)
        ta = re.match(r"^(\s*)([A-Za-z_]\w*): TypeAlias\s*$", raw)
        if ta:
            ta_indent = ta.group(1)
            ta_name = ta.group(2)
            if ta_indent == "" and ta_name in info.get("annotated_type_aliases", {}):
                new_lines.append(f"{ta_name}: TypeAlias = {info['annotated_type_aliases'][ta_name]}")
            else:
                new_lines.append(raw)
            continue

        # Check for bare unparameterized collection types at module level
        bare_coll = re.match(r"^([A-Za-z_]\w*): (dict|list|set|tuple)\s*$", raw)
        if bare_coll:
            bare_name = bare_coll.group(1)
            bare_type = bare_coll.group(2)
            inferred = info.get("annotations", {}).get(bare_name, "")
            if inferred.startswith(bare_type + "["):
                new_lines.append(f"{bare_name}: {inferred}")
            else:
                new_lines.append(raw)
            continue

        # Check for narrowed T | None -> T (must come before Incomplete check)
        na = re.match(r"^(\s*)([A-Za-z_]\w*): (.+) \| None\s*$", raw)
        if na:
            na_indent, na_name, na_base = na.group(1), na.group(2), na.group(3)
            current_class_for_na = None
            for ci in sorted(class_at_indent.keys(), key=len, reverse=True):
                if len(na_indent) > len(ci):
                    current_class_for_na = class_at_indent[ci]
                    break
            if current_class_for_na:
                narrowed_dict = info.get("narrowed_class_attrs", {}).get(current_class_for_na, {})
                if na_name in narrowed_dict and narrowed_dict[na_name] == na_base:
                    new_lines.append(f"{na_indent}{na_name}: {na_base}")
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
    """Return set of all names imported in the stub text (handles multi-line imports)."""
    try:
        tree = ast.parse(txt)
    except SyntaxError:
        return set()
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
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


def ensure_any_import(txt):
    """Add 'from typing import Any' if Any is used as a type but not yet imported."""
    if not re.search(r"(?<![\"'\w])Any(?!\w)", txt):
        return txt
    if re.search(r"from typing import\b.*\bAny\b", txt):
        return txt
    lines = txt.split("\n")
    # Try to extend an existing 'from typing import ...' line
    for i, line in enumerate(lines):
        if line.startswith("from typing import "):
            names = [n.strip() for n in line[len("from typing import "):].split(",")]
            if "Any" not in names:
                lines[i] = "from typing import " + ", ".join(sorted(names + ["Any"]))
            return "\n".join(lines)
    # Insert after the last import line
    last_import_idx = -1
    for i, line in enumerate(lines):
        if line.startswith(("import ", "from ")):
            last_import_idx = i
    insert_at = last_import_idx + 1 if last_import_idx >= 0 else 0
    lines.insert(insert_at, "from typing import Any")
    return "\n".join(lines)


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


# ---------------------------------------------------------------------------
# Sublime Text libs baseline
# ---------------------------------------------------------------------------

def _load_sublime_baseline(sublime_libs_dir):
    """Load class_attrs from sublime-text-libs as a baseline for cross-module resolution."""
    baseline = {"class_attrs": {}, "class_methods": {}}
    for py_file in sorted(sublime_libs_dir.rglob("*.py")):
        info = collect_source_info(py_file)
        if info:
            for cls, attrs in info.get("class_attrs", {}).items():
                if cls not in baseline["class_attrs"]:
                    baseline["class_attrs"][cls] = {}
                baseline["class_attrs"][cls].update(attrs)
            for cls, methods in info.get("class_methods", {}).items():
                if cls not in baseline["class_methods"]:
                    baseline["class_methods"][cls] = {}
                baseline["class_methods"][cls].update(methods)
    return baseline


SUBLIME_BASELINE: dict | None = None


def get_sublime_baseline(sublime_libs_dir):
    """Lazy-load the sublime baseline once."""
    global SUBLIME_BASELINE
    if SUBLIME_BASELINE is None:
        SUBLIME_BASELINE = _load_sublime_baseline(sublime_libs_dir)
    return SUBLIME_BASELINE


# ---- Main ----
SCRIPT_DIR = pathlib.Path(__file__).parent
out = pathlib.Path(os.environ["LSP_OUT"])
lsp_src = pathlib.Path(os.environ["LSP_SRC"])

# Pre-load sublime-text-libs as a type baseline for cross-module resolution
sublime_libs_dir = SCRIPT_DIR.parent / "sublime-text-libs" / "python38"
baseline = get_sublime_baseline(sublime_libs_dir) if sublime_libs_dir.is_dir() else None

for pyi in sorted(out.rglob("*.pyi")):
    txt = pyi.read_bytes().decode("utf-8").replace("\r\n", "\n")

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

    info = collect_source_info(src, baseline) if src else None

    needs_fix = (
        ": Incomplete" in txt
        or bool(re.search(r"\w+: TypeAlias\s*$", txt, re.MULTILINE))
        or bool(re.search(r"^\w+: (?:dict|list|set|tuple)\s*$", txt, re.MULTILINE))
        or bool(info and info.get("narrowed_class_attrs"))
    )
    if not needs_fix:
        continue

    if info:
        txt = apply_fixes(txt, info)
        txt = add_missing_imports(txt, info)
        txt = ensure_any_import(txt)
        txt = cleanup_incomplete_import(txt)

    pyi.write_bytes(txt.encode("utf-8"))
