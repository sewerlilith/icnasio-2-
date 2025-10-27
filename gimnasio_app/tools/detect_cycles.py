"""Detect import cycles among local Python modules in the project.

Scans .py files under this package directory and builds a graph of imports between
local modules (based on relative paths). Then runs DFS to find cycles and prints them.
"""
import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]  # gimnasio_app/
# Exclude virtualenvs or hidden folders
py_files = list(ROOT.rglob('*.py'))

# map module key (relative posix path) -> file path
modules = {str(p.relative_to(ROOT).as_posix()): p for p in py_files}

# parse imports
imports = {m: set() for m in modules}

for mod, path in modules.items():
    try:
        src = path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Could not read {path}: {e}", file=sys.stderr)
        continue
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        print(f"Syntax error parsing {path}: {e}", file=sys.stderr)
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports[mod].add(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                # handle relative imports like .services
                level = node.level
                module_name = node.module
                if level:
                    # resolve to relative path
                    # compute package path from mod
                    base = pathlib.Path(mod)
                    parts = base.parts
                    if len(parts) >= level:
                        target_parts = parts[: -level]
                    else:
                        target_parts = []
                    if module_name:
                        target_parts = target_parts + tuple(module_name.split('.'))
                    if target_parts:
                        candidate = '/'.join(target_parts) + '.py'
                        imports[mod].add(candidate)
                    else:
                        # top-level
                        imports[mod].add(module_name)
                else:
                    imports[mod].add(node.module)

# Try to normalize imports to local module keys when possible
# We'll consider an import matches a module if its dotted name corresponds to a path
# e.g. "services.rutina_service" -> "services/rutina_service.py"

def name_to_key(name):
    if not name:
        return None
    # remove as alias
    name = name.split(' as ')[0]
    parts = name.split('.')
    # try progressive
    candidates = []
    for i in range(len(parts), 0, -1):
        candidate = '/'.join(parts[:i]) + '.py'
        candidates.append(candidate)
    for c in candidates:
        if c in modules:
            return c
    return None

graph = {m: set() for m in modules}
for m, imps in imports.items():
    for im in imps:
        if im.endswith('.py') and im in modules:
            graph[m].add(im)
            continue
        key = name_to_key(im)
        if key:
            graph[m].add(key)

# now detect cycles using DFS
visited = set()
stack = []
cycles = set()

def dfs(node, path):
    if node in path:
        idx = path.index(node)
        cycle = path[idx:] + [node]
        # canonicalize cycle representation
        cyc = tuple(cycle)
        cycles.add(cyc)
        return
    if node in visited:
        return
    path.append(node)
    for nbr in graph.get(node, ()): 
        dfs(nbr, path)
    path.pop()
    visited.add(node)

for node in graph:
    dfs(node, [])

if not cycles:
    print("No import cycles detected among local modules.")
else:
    print(f"Detected {len(cycles)} cycle(s):")
    for c in cycles:
        print('  -> '.join(c))

# Also print a small summary of edges
print('\nSummary: edges between local modules (showing only edges to local files)')
for m, neigh in graph.items():
    if neigh:
        print(f"{m} -> {', '.join(sorted(neigh))}")
